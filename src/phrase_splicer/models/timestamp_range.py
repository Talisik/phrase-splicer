from dataclasses import dataclass

from .timestamp import Timestamp


@dataclass(frozen=True)
class TimestampRange:
    """
    Example:

    The = [0, 1]

    2s Pause

    big = [3, 4]

    0s Pause

    brown = [4, 6]

    1s Pause

    fox = [7, 8]

    ```
    The                      big brown    fox = 4 words
    Ang ma-la-king ka-yu-mang-gi so-ro he-llo = 5 words
    ###......................###.#####....###
    ```

    Ang = [0, 1]

    2s Pause

    ma-la-king = [3, 4]

    0s Pause
    """

    start: Timestamp
    end: Timestamp

    @property
    def duration(self):
        """
        The duration of the timestamp range in milliseconds, calculated as the difference
        between the end and start timestamps.
        """

        return self.end.milliseconds - self.start.milliseconds

    def get_distance(self, other: "TimestampRange"):
        """
        Returns the distance between two timestamp ranges in milliseconds.

        If the timestamp ranges overlap, the distance is 0.
        """
        if self.start.milliseconds < other.start.milliseconds:
            return max(0, other.start.milliseconds - self.end.milliseconds)

        return max(0, self.start.milliseconds - other.end.milliseconds)

    def get_intersection_duration(self, other: "TimestampRange"):
        """
        Calculates the intersection of the two timestamp ranges in milliseconds.

        The intersection is calculated by finding the overlap of the two timestamp ranges. The overlap is
        calculated by finding the latest start time and the earliest end time, and then subtracting the start
        from the end. If the overlap is negative, it is set to 0.

        Args:
            other (TimestampRange): The other timestamp range to calculate the intersection with.

        Returns:
            float: The intersection of the two timestamp ranges in milliseconds.
        """
        latest_start = max(self.start.milliseconds, other.start.milliseconds)
        earliest_end = min(self.end.milliseconds, other.end.milliseconds)

        return max(0, earliest_end - latest_start)

    def get_intersection_percent(
        self,
        other: "TimestampRange",
    ) -> float:
        """
        Calculates the intersection of the two timestamp ranges as a fraction of the total duration.

        The intersection is calculated by finding the overlap of the two timestamp ranges, and then dividing
        it by the total duration of the two timestamp ranges. The total duration is calculated as the sum of
        the individual durations minus the overlap.

        If the total duration is 0, the function returns 0.

        :param other: The other timestamp range to calculate the intersection with.
        :type other: TimestampRange
        :return: The intersection of the two timestamp ranges as a fraction of the total duration.
        :rtype: float
        """
        overlap_duration = self.get_intersection_duration(other)
        total_duration = self.duration + other.duration - overlap_duration

        return overlap_duration / total_duration if total_duration > 0 else 0
