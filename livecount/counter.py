#
# Copyright 2011 Greg Bayer <greg@gbayer.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from google.appengine.ext import db
from google.appengine.api.labs import taskqueue
from google.appengine.api import memcache
from google.appengine.ext import webapp
import logging
import wsgiref.handlers

""" 
  Live-Count is a memcache-based counter api with asyncronous writes to persist counts to datastore.
  
  Semantics:
   - Write-Behind
   - Read-Through
"""


class LiveCountCounter(db.Model):
    count = db.IntegerProperty()
    namespace = db.StringProperty(default="default")
    
    @staticmethod
    def KeyName(name, namespace):
        return namespace + ':' + name


def LoadAndGetCount(name, namespace='default'):
    #logging.info("Getting counter, name = " + name + ", namespace = " + namespace)
    count =  memcache.get(name, namespace=namespace) 
    if count is None:
        # See if this counter already exists in the datastore
        key = LiveCountCounter.KeyName(name, namespace)
        record = LiveCountCounter.get_by_key_name(key)
        count = None
        # If counter exists in the datastore, but is not currently in memcache, add it
        if record:
            count = record.count
            memcache.add(name, count, namespace=namespace)
    return count

def LoadAndIncrementCounter(name, delta, namespace='default', batch_size=None):
    """
    Setting batch size allows control of how often a writeback worker is created.
    By default, this happens at every increment to ensure maximum durability.
    If there is already a worker waiting to write the value of a counter, another will not be created.
    """
    #logging.info("Incrementing counter, name = " + name)
    # Warning: There is a race condition here. If two processes try to load
    # the same value from the datastore, one's update may be lost.
    # TODO: Think more about whether we care about this...
    current_count = None
    if memcache.incr(name, delta, namespace=namespace) is None:
        # See if this counter already exists in the datastore
        key = LiveCountCounter.KeyName(name, namespace)
        record = LiveCountCounter.get_by_key_name(key)
        if record:
            # Load last value from datastore
            memcache.add(name, record.count + delta, namespace=namespace)
            if batch_size: current_count = record.count
        else:
            # Start new counter
            memcache.add(name, delta, namespace=namespace)
            if batch_size: current_count = delta
    else:
        if batch_size: current_count = memcache.get(name, namespace=namespace)
    # If batch_size is set, only try creating one worker per batch
    if not batch_size or (batch_size and current_count % batch_size == 0):
        if memcache.add(name + '_dirty', delta, namespace=namespace):
            #logging.info("Adding task to taskqueue. counter value = " + str(memcache.get(name, namespace=namespace)))
            taskqueue.add(queue_name='writebacks', url='/livecount/worker', params={'name': name, 'namespace': namespace})


def LoadAndDecrementCounter(name, delta, namespace='default', batch_size=None):
    #logging.info("Decrementing counter, name = " + name)
    LoadAndIncrementCounter(name, -delta, namespace, batch_size)
   

class LiveCountCounterWorker(webapp.RequestHandler):
    def post(self):
        #logging.info("Running LiveCountCounterWorker...")
        name = self.request.get('name')
        namespace = self.request.get('namespace')
        key = LiveCountCounter.KeyName(name, namespace)
        #logging.info("Worker for name = " + name + ", namespace = " + namespace + ", key = " + key)
        memcache.delete(name + '_dirty', namespace=namespace)
        value = memcache.get(name, namespace=namespace)
        if value is None:
            logging.error('LiveCountCounterWorker: Failure for key=%s', key)
            return
        LiveCountCounter(key_name=key, count=value, namespace=namespace).put()


class ClearEntireCacheHandler(webapp.RequestHandler):
    """ Clears entire memcache
    """
    
    def get(self):
        logging.info("Deleting all counters in memcache. Any counts not previously flushed will be lost.")
        result=in_memory_counter.ClearEntireCache()
        self.response.out.write("Done. ClearEntireCache succeeded = " + str(result))
      
class WritebackAllCountersHandler(webapp.RequestHandler):
    """ Writes back all counters from memory to the datastore
    """
    
    def get(self):
        namespace = self.request.get('namespace')
        delete = self.request.get('delete')
        logging.info("Writing back all counters from memory to the datastore. Namespace=%s. Delete from memory=%s." % (str(namespace), str(delete)))
        result = False
        while not result:
            result=in_memory_counter.WritebackAllCounters(namespace, delete)
        
        self.response.out.write("Done. WritebackAllCounters succeeded = " + str(result))
    
class GetCountHandler(webapp.RequestHandler):
    """ Get counter value from memcache or datastore
    """
    
    def get(self):
        name = self.request.get('name')
        namespace = self.request.get('namespace')
        count = counter.LoadAndGetCount(name, namespace)
        if count:
            self.response.set_status(200) 
            self.response.out.write(count)
        else:
            self.response.set_status(404)
            
class RedirectToCounterAdminHandler(webapp.RequestHandler):
    """ For convenience / demo purposes, redirect to counter admin page.
    """
    def get(self):
        self.redirect('/livecount/counter_admin')
            
def GetMemcacheStats():
    stats = memcache.get_stats()
    return stats


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([
         ('/livecount/worker', LiveCountCounterWorker),
         ('/livecount/clear_entire_cache', ClearEntireCacheHandler),
         ('/livecount/writeback_all_counters', WritebackAllCountersHandler),
         ('/livecount/get_count', GetCountHandler),
         ('/', RedirectToCounterAdminHandler)
    ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
