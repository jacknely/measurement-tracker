#!/usr/bin/env python

from measurementTracker import create_app
from dbinit import create_and_load

app = create_app('measurementTracker.config.DevConfig')

create_and_load()
