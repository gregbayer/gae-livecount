from datetime import datetime
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from livecount import counter
from livecount.counter import LivecountCounter
from livecount.counter import PeriodType


def count(name):
    counter.load_and_increment_counter(name)


def advanced_count(name):
    counter.load_and_increment_counter(name, datetime.now(), period_types=[PeriodType.DAY, PeriodType.WEEK], namespace="tweet", delta=1)


class MainHandler(webapp.RequestHandler):
    def get(self):
        try:
            name = "visitor"
            counter.load_and_increment_counter(name)
        except:
            logging.info(repr(error))
        self.response.out.write('Visitor: ' + str(counter.load_and_get_count(name)))

    
def main():
    application = webapp.WSGIApplication(
    [  
        ('/examples', MainHandler),
    ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
