# Copyright (c) 2011, Kevin Bortis
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#    3. Neither the names of the copyright holders nor the names of any
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Get the difference of Days betwen today and 9.April 1984
from datetime import date, datetime, timedelta
from math import floor
import belib.format.base23 as base23

# Privat funktion to encode a timedelta to be datestrings
def __encodeToDict(delta):
	# The new week has 23days. Calculating the weeks since 9.April 1984
        beWeek = int(floor(delta.days/23))
        #calculate seconds since last full beWeek
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

