from dataclasses import dataclass
from typing import Callable, Iterable, List, TypeVar

import syllables

from .timestamp_range import TimestampRange
from .item import Item
from .timestamp import Timestamp

T = TypeVar("T")


@dataclass(frozen=True)
class Word:
    text: str
    timestamp: TimestampRange

    @property
    def syllables_count(self):
        return syllables.estimate(self.text)

    @classmethod
    def make(
        cls,
        items: Iterable[T],
        text_selector: Callable[[T], str],
        timestamp_start_selector: Callable[[T], Timestamp],
        timestamp_end_selector: Callable[[T], Timestamp],
    ):
        """
        Creates an iterable of Word objects from an iterable of items, where each item is converted into a Word by selecting its text and timestamp using the provided selectors.

        Args:
            items: An iterable of items to convert into words.
            text_selector: A function that takes an item and returns its text.
            timestamp_start_selector: A function that takes an item and returns its start timestamp.
            timestamp_end_selector: A function that takes an item and returns its end timestamp.

        Returns:
            An iterable of Word objects.
        """
        return (
            cls(
                text=text_selector(item),
                timestamp=TimestampRange(
                    start=timestamp_start_selector(item),
                    end=timestamp_end_selector(item),
                ),
            )
            for item in items
        )

    @classmethod
    def distribute(
        cls,
        items: List[Item],
        start: float,
        total_duration: float,
    ):
        total_weight = sum(item.weight for item in items)
        a = start

        for item in items:
            duration = (item.weight / total_weight) * total_duration
            b = a + duration

            yield cls(
                text=item.text,
                timestamp=TimestampRange(
                    start=Timestamp(a),
                    end=Timestamp(b),
                ),
            )

            a = b

    @classmethod
    def distribute_by_characters(
        cls,
        words: List[str],
        start: Timestamp,
        end: Timestamp,
    ):
        return cls.distribute(
            items=[
                Item(
                    text=word,
                    weight=len(word),
                )
                for word in words
            ],
            start=start.seconds,
            total_duration=end.seconds - start.seconds,
        )

    @classmethod
    def distribute_by_syllables(
        cls,
        words: List[str],
        start: Timestamp,
        end: Timestamp,
    ):
        return cls.distribute(
            items=[
                Item(
                    text=word,
                    weight=syllables.estimate(word),
                )
                for word in words
            ],
            start=start.seconds,
            total_duration=end.seconds - start.seconds,
        )
