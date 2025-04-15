from dataclasses import dataclass


@dataclass(frozen=True)
class Timestamp:
    milliseconds: int

    @property
    def seconds(self):
        return self.milliseconds / 1000

    @property
    def text(self):
        """
        Returns the timestamp formatted as a string in the format 'HH:MM:SS.mmm',
        where HH is hours, MM is minutes, SS is seconds, and mmm is milliseconds.
        """

        hr = int(self.seconds // 3600)
        mn = int((self.seconds % 3600) // 60)
        sc = int(self.seconds % 60)
        ms = self.milliseconds % 1000

        return f"{hr:02}:{mn:02}:{sc:02}.{ms:03}"

    @classmethod
    def from_text(cls, text: str):
        """
        Creates a Timestamp from a string in the format 'HH:MM:SS.mmm'. The string
        is parsed and converted to a float representing the timestamp in milliseconds.
        """

        hours, minutes, sec_millis = text.split(":")
        sec, millis = sec_millis.split(".")

        return int(hours) * 3600 + int(minutes) * 60 + int(sec) + int(millis) / 1000
