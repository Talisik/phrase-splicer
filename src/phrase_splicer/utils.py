from typing import Dict, Iterable, List, Optional

from phrase_slicer.models.timestamp_range import TimestampRange

from .models.word import Word


def get_pauses(words: Iterable[Word]):
    """
    Yields timestamp ranges of pauses between words.

    Args:
        words: An iterable of words to get pauses from.

    Yields:
        TimestampRange: A timestamp range of a pause between words.
    """
    prev_word: Optional[Word] = None

    for word in words:
        if not prev_word:
            prev_word = word
            continue

        range = TimestampRange(
            start=prev_word.timestamp.end,
            end=word.timestamp.start,
        )

        if range.duration > 0:
            yield range

        prev_word = word


def splice_by_syllables(
    reference_words: List[Word],
    new_words: List[Word],
):
    pauses = [*get_pauses(reference_words)]

    normalized = Word.distribute_by_syllables(
        words=[word.text for word in new_words],
        start=reference_words[0].timestamp.start,
        end=reference_words[-1].timestamp.end,
    )

    word_map: Dict[Word, List[Word]] = {
        reference_word: [] for reference_word in reference_words
    }

    for word in normalized:
        nearest_reference_word, _ = max(
            word_map.items(),
            key=lambda map: map[0].timestamp.get_intersection_percent(
                word.timestamp,
            )
            / (sum(word.syllables_count for word in map[1]) + 1),
        )

        word_map[nearest_reference_word].append(word)

    return word_map
