import logging
from livecount import counter


def count(name):
    counter.load_and_increment_counter(name, 1)


def advanced_count(name):
    counter.load_and_increment_counter(name, datetime.now(), period_types=[PeriodType.DAY, PeriodType.WEEK], namespace="tweet", 1)
