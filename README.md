# About

Live-Count is a fast and simple implementation of real-time counters for Google AppEngine.  The goal is to support the counting of real-time events such as impressions, clicks, conversions, and other user actions and to do so in an efficient and scalable way.  Since Live-Count increments counts in memory, it is  almost always faster than basic sharded counters, potentially trading off some consistency and durability.  To ensure maximum consistency and durability, by default Live-Count attempts to asynchronously write each update to the datastore.

Live-Count counters are extremely simple to use.  Just import the module and call "LoadAndIncrementCounter" with a key name and increment delta.  Live-Count also supports arbitrary string keys allowing more complex character-delimited hierarchal key and supports the use of appengine's memcache namespaces maintain separate counters with the same key.

# Getting started

To try Live-Count:
1. Make sure you have the latest version of the Google AppEngine python sdk
2. git clone git://github.com/gregbayer/live-count.git
3. Point the appengine launcher at the live-count directory and start the project locally
4. Navigate to http://localhost:8080/counter/counter_admin
5. Choose to login as an administrator

To add Live-Count to your project:
1. git clone git://github.com/gregbayer/live-count.git
2. Add entries to your app.yaml and queue.yaml based on included files.
3. Copy the live-count directory into your appengine project
4. Include "from counters import write_behind_counter" at the top of you python file
5. Call write_behind_counter.LoadAndIncrementCounter(...) as in example.py

# Performance and CAP tradeoffs

Live-Count makes extensive use of Google AppEngine's memcache implementation.  This allows maximum performance, while leaving counts vulnerable to a memcache eviction.  This risk is mitigated by using Google AppEngine's taskqueue to asynchronous write the value of a count back to the datastore after any change.  To avoid unnecessary overhead, a new asynchronous worker is only created if one is not already waiting to update a giving counter's value.  If one is already in the queue, it simply writes back the most recent count.  The resulting risk of lost counts is minimal and acceptable for many real-time counter use cases.

If writeback loads are higher than desired on frequently updated counters, Live-Count includes the option to delay writebacks until a given batch size is reached.  This effectively allows the developer to select the appropriate tradoff between performance and tolerance for lost counts each time a counter is incremented.

# Usage at Pulse

Live-Counts has been used extensively at [Pulse News](http://pulsene.ws) for counting everything from share and click events to mobile client A/B test results. 

# Other Projects and Information

Live-Count is by no means the first or only attempt at real-time counters.  Here are a few interesting links:

* [Sharded Counters](http://code.google.com/appengine/articles/sharding_counters.html)
* [Brett Slatkin's Google I/O talk](http://sites.google.com/site/io/building-scalable-web-applications-with-google-app-engine)
* [Effective memcache](http://code.google.com/appengine/articles/scaling/memcache.html)
* [Google Cookbook](http://appengine-cookbook.appspot.com/recipe/high-concurrency-counters-without-sharding/)
* [fastpageviews](http://code.google.com/p/fastpageviews/)



