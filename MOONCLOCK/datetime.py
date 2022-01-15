from adafruit_datetime import *


class RTC:

    def __init__(self, requests):
        self.requests = requests

    @property
    def datetime(self):
        print('Loading current time from worldtimeapi.org')
        dt = datetime.fromisoformat(
            self.requests.get('http://worldtimeapi.org/api/timezone/Etc/UTC', timeout=5).json()['datetime'])
        print('Loaded current time from worldtimeapi.org: ', dt)

        return dt.timetuple()


class datetime(datetime):
    @classmethod
    def fromtimestamp(cls, timestamp, tz=None):
        return cls._fromtimestamp(timestamp, False, tz)


def tz(requests, timezone):
    print('Loading', timezone, 'timezone data from worldtimeapi.org')
    offset = requests.get('http://worldtimeapi.org/api/timezone/{}'.format(timezone), timeout=5).json()['raw_offset']
    print('Loaded', timezone, 'timezone data from worldtimeapi.org:', offset)

    class dynamictzinfo(tzinfo):
        _offset = timedelta(seconds=offset)

        def utcoffset(self, dt):
            return self._offset

        def tzname(self, dt):
            return timezone

    return dynamictzinfo()
