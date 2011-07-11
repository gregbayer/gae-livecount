from datetime import datetime
import logging

from livecount import counter
from livecount.counter import LivecountCounter
from livecount.counter import PeriodType


def count(name):
    counter.load_and_increment_counter(name, 1)


def advanced_count(name):
    counter.load_and_increment_counter(name, datetime.now(), period_types=[PeriodType.DAY, PeriodType.WEEK], namespace="tweet", 1)
