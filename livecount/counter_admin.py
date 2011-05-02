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



import os
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from livecount import write_behind_counter
from livecount.write_behind_counter import WriteBehindCounter
import logging
import simplejson

#counter_list = []

class CounterHandler(webapp.RequestHandler):
  """Handles displaying the values of the counters
  and requests to increment/decrement counters.
  """

  def get(self):
    counter_name = self.request.get('counter_name')
    namespace = self.request.get('namespace')
    if not namespace:
        namespace = "default"
    delta = self.request.get('delta')
    if not delta:
      delta = 0
    logging.info("getting WriteBehindCounters for namespace = " + str(namespace))
    modified_counter = None
    if counter_name:
      modified_counter = WriteBehindCounter.get_by_key_name(namespace + ":" + counter_name)
    
    counter_entities_query = WriteBehindCounter.all().filter("namespace = ", namespace).order('-count')
    counter_entities = counter_entities_query.fetch(20)
    logging.info("counter_entities: " + str(counter_entities))
    
    stats = write_behind_counter.GetMemcacheStats()
    template_values = {
      'namespace': namespace,
      'counters': counter_entities,
      'modified_counter': modified_counter,
      'counter_name': counter_name,
      'delta': delta,
      'stats': stats
    }
    logging.info("template_values: " + str(template_values))
    template_file = os.path.join(os.path.dirname(__file__), 'counter_admin.html')
    self.response.out.write(template.render(template_file, template_values))

  def post(self):
    global counter_list
    counter_name = self.request.get('counter')
    namespace = self.request.get('namespace')
    delta = self.request.get('delta')
    type = self.request.get('type')
#    if counter_name not in counter_list:
#        counter_list.append(counter_name)
#    logging.info("counter_list: " + str(counter_list))
    if type == "Increment Counter":
      write_behind_counter.LoadAndIncrementCounter(counter_name, long(delta), namespace=namespace)
    elif type == "Decrement Counter":
      write_behind_counter.LoadAndDecrementCounter(counter_name, long(delta), namespace=namespace)
    self.redirect("/livecount/counter_admin?namespace=" + namespace + "&counter_name=" + counter_name + "&delta=" + delta)


class GetCounterHandler(webapp.RequestHandler):
  """Handles displaying the values of the counters
  and requests to increment/decrement counters.
  """

  def get(self):
    counter_name = self.request.get('counter_name')
    namespace = self.request.get('namespace')
    if not namespace:
        namespace = "share_domain_count"
    fetch_limit = self.request.get('fetch_limit')
    if not fetch_limit:
        fetch_limit = "20"
    
    if counter_name:
        logging.info("querying counter directly for counter_name = " + str(counter_name) + ", namespace = " + str(namespace))
        count = write_behind_counter.LoadAndGetCount(counter_name, namespace=namespace)
        
        self.response.set_status(200)
        self.response.out.write(count)
    else:
        logging.info("querying datastore for WriteBehindCounters for counter_name = " + str(counter_name) + ", namespace = " + str(namespace))
        counter_entities_query = WriteBehindCounter.all().order('-count')
        if counter_name:
            counter_entities_query.filter("counter_name = ", counter_name)
        if namespace:
            counter_entities_query.filter("namespace = ", namespace)
        counter_entities = counter_entities_query.fetch(int(fetch_limit))
        logging.info("counter_entities: " + str(counter_entities))

        counters = []
        for entity in counter_entities:
            counter_data = {'key': str(entity.key().name()),
                            'count': str(entity.count)}
            counters.append(counter_data)
        json_counters_data = simplejson.dumps(counters)
            
        if json_counters_data:
            self.response.set_status(200)
            self.response.out.write(json_counters_data)
            return


def main():
  application = webapp.WSGIApplication(
  [  
    ('/livecount/counter_admin', CounterHandler),
    ('/livecount/get_counter', GetCounterHandler),
  ], debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()