import logging
from livecount import counter


def count_event(event):
    counter.LoadAndIncrementCounter(event, 1)


def advanced_event_counts(type, device, url, version):
    batch_size = None
    if type == 'impression': batch_size = 10
    domain = extract_feed_domain(story_url);
    namespace = "website_" + version
#    logging.info("Bar " + type + " for device: " + device + ", domain: " + domain)
    counter.LoadAndIncrementCounter(type, 1, namespace, batch_size)
    counter.LoadAndIncrementCounter(type + "__" + device, 1, namespace, batch_size)
    counter.LoadAndIncrementCounter(type + "__" + device + "__" + domain, 1, namespace, batch_size)

