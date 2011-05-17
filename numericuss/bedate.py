#!/usr/bin/python
# Get the difference of Days betwen today and 9.April 1984
from datetime import date, datetime, timedelta
from math import floor
import base23

# Privat funktion to encode a timedelta to be datestrings
def __encodeToDict(delta):
	# The new week has 23days. Calculating the weeks since 9.April 1984
        beWeek = int(floor(delta.days/23))
        #calculate seconds since last full bweek
        beSeconds = (delta.days%23)*86400 + delta.seconds
        # Convert to base23
        # alphabet: 23456789abcdefhkmstvwxz
        beWeek = base23.encode(beWeek)
        beSeconds = base23.encode(beSeconds)
        return {'beWeek': beWeek, 'beSeconds': beSeconds}

# Returns timedelta since epoch
def getBeDateDelta(date=datetime.now()):
	fromDate = datetime(1984, 4, 9, 6, 45)
    return date-fromDate

# Returns encoded be datestrings as dict
def getBeDate(date=datetime.now()):
    delta = getBeDateDelta(date)
	return __encodeToDict(delta)

# Return a timestamp in seconds since epoch
def getBeStamp(date=datetime.now()):
	delta = getBeDateDelta(date)
	# return delta.total_seconds() # Activate on Python 2.7 or higher
	return (delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 10**6) / 10**6

# Encodes a be timestamp and returns a be datestring
def getBeStampEnc(beStamp):
	delta = timedelta(0,beStamp)
	return __encodeToDict(delta)

