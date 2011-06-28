# About

Livecount is a fast and simple implementation of real-time counters for Google AppEngine.  The goal is to support the counting of real-time events such as impressions, clicks, conversions, and other user actions and to do so in an efficient and scalable way.  Since Livecount increments counts in memory, it is almost always faster than basic sharded counters, potentially trading off some consistency and durability.  To ensure maximum consistency and durability, by default Livecount attempts to asynchronously write each update to the datastore.

Livecount counters are extremely simple to use.  Just import the module and call load_and_increment_counter with a key name and increment delta.  Optional parameters include the period, for specifying the desired datetime of saved key name, and period_type, for specifying the granularity of the count (seconds, minutes, hours, days, weeks, months, and years).  Livecount counters are based on simple string keys and support namespaces to maintain separate counters with the same key. Since arbitrary strings are supported, character-delimited hierarchal keys can be used to further group related counters.

# Getting started

To try Livecount:

1. Make sure you have the latest version of the Google AppEngine python sdk
2. git clone git://github.com/gregbayer/gae-livecount.git
3. Point the appengine launcher at the livecount directory and start the project locally
4. Navigate to http://localhost:8080/livecount/counter_admin
5. Choose to login as an administrator

To add Livecount to your AppEngine project:

1. git clone git://github.com/gregbayer/gae-livecount.git
2. Add entries to your app.yaml and queue.yaml based on included files.
3. Copy the livecount directory into your appengine project
4. Include "from livecount import counter" at the top of you python file
5. Call counter.load_and_increment_counter(...) as in example.py

# Performance and CAP tradeoffs

Livecount makes extensive use of Google AppEngine's [memcache implementation](http://code.google.com/appengine/docs/python/memcache/overview.html).  This allows maximum performance, while leaving counts vulnerable to a memcache eviction.  This risk is mitigated by using Google AppEngine's [taskqueue](http://code.google.com/appengine/docs/python/taskqueue/overview.html) to asynchronous write the value of a count back to the datastore after any change.  To avoid unnecessary overhead, a new asynchronous worker is only created if one is not already waiting to update a giving counter's value.  If one is already in the queue, it simply writes back the most recent count.  The resulting risk of lost counts is minimal and acceptable for many real-time counter use cases.

If writeback loads are higher than desired on frequently updated counters, Livecount includes the option to delay writebacks until a given batch size is reached.  This allows the developer to select the appropriate tradoff between performance and tolerance for lost counts each time a counter is incremented.

There is also a potential race condition in the load_and_increment_counter function on line 57 of [counter.py](https://github.com/gregbayer/gae-livecount/blob/master/livecount/counter.py).  Here the concern is that if two processes try to load the same value from the datastore (because it is not in the memcache, and two update requests come in simultaneously), one's update may be lost.  This could be avoided by wrapping the critical section in a transaction, at the cost of some performance.  In practice, this is rarely a problem, since counters that are frequently updated usually stay resident in memcache and counters that are infrequently updated are unlikely to have two updates come in at the same time. For some applications, the potential for lost updates is unacceptable. In these cases, it would make sense to use AppEngine's [transaction mechanism](http://code.google.com/appengine/docs/python/datastore/transactions.html) here.

# Scalability Limiatations

One factor that affects Livecount's scalability is the rate at which appengine task queues can writeback counter updates (xxx tasks/second per queue). See [Quotas and Limits for Push Queues](http://code.google.com/appengine/docs/python/taskqueue/overview-push.html) for more information.  To effectively increase this limit, Livecount could be extended to use more than one named queue. 

The maximum number of queues could also be reached.  At this point, a different writeback strategy should be used.  One option would be to batch updates for several different counters in one memcache object and only create a writeback worker when the batch size is reached.

# Usage at Pulse

Livecounts has been used extensively at [Pulse News](http://pulsene.ws) for counting everything from share and click events to mobile client A/B test results. 

# Other Projects and Information

Livecount is by no means the first or only attempt at real-time counters.  Here are a few interesting links:

* [Sharded Counters](http://code.google.com/appengine/articles/sharding_counters.html)
* [Brett Slatkin's Google I/O talk](http://sites.google.com/site/io/building-scalable-web-applications-with-google-app-engine)
* [Effective memcache](http://code.google.com/appengine/articles/scaling/memcache.html)
* [Google Cookbook](http://appengine-cookbook.appspot.com/recipe/high-concurrency-counters-without-sharding/)
* [fastpageviews](http://code.google.com/p/fastpageviews/)
* [Rainbird (Kevin Weil / Twitter)](http://www.slideshare.net/kevinweil/rainbird-realtime-analytics-at-twitter-strata-2011)


