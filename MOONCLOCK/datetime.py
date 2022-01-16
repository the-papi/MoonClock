from adafruit_datetime import *


class RTC:

    def __init__(self, requests):
        self.requests = requests

    @property
    def datetime(self):
        print('Loading current time from worldtimeapi.org')
        dt = datetime.fromisoformat(
            self.requests.get('http://worldtimeapi.org/api/timezone/Etc/UTC', timeout=15).json()['datetime'])
        dt._tzinfo = None
        print('Loaded current time from worldtimeapi.org: ', dt)

        return dt.timetuple()


class datetime(datetime):
    @classmethod
    def fromtimestamp(cls, timestamp, tz=None):
        return cls._fromtimestamp(timestamp, False, tz)


def tz(requests, tzname):
    print('Loading', tzname, 'tzname data from worldtimeapi.org')
    offset = requests.get('http://worldtimeapi.org/api/timezone/{}'.format(tzname), timeout=15).json()['raw_offset']
    print('Loaded', tzname, 'tzname data from worldtimeapi.org:', offset)

    class dynamictimezone(timezone):

        def __new__(cls, *args, **kwargs):
            return super().__new__(cls, timedelta(seconds=offset), name=tzname)

    return dynamictimezone()
