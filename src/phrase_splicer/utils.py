import re
from typing import Dict, Iterable, List, Optional, Union

from .constants import kks, ur
from .models.timestamp_range import TimestampRange
from .models.word import Word


def romanize(text: str) -> str:
    """
    Romanizes the input text based on its language.

    This function first attempts to romanize Japanese text using pykakasi. If the input
    text is not modified after this conversion, it is assumed not to be Japanese, and
    the function then attempts to romanize the text using Uroman for other languages.

    Args:
        text: The input text string to be romanized.

    Returns:
        The romanized version of the input text. If the text is Japanese, it returns
        the original text.
    """

    new_text = " ".join(value for obj in kks().convert(text) for value in obj.values())

    if text != new_text:
        # Text is Japanese.
        return text

    # Text is not Japanese, try other languages to romanize.

    return ur().romanize_string(text)  # type: ignore


def split_words(
    text: str,
    rx: Union[str, re.Pattern[str]] = r"[\w-']+",
):
    return re.split(rx, text)


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


def splice_evenly(
    reference_words: List[Word],
    new_words: List[str],
):
    """
    Splices a list of new words into reference words evenly based on their position.

    This function maps each new word to a reference word, distributing them as evenly as possible
    across the reference words, and generates Word objects with timestamps matching those of
    the reference words. It then distributes these words by syllables within the time range of
    each reference word.

    Args:
        reference_words: A list of Word objects serving as reference for distribution.
        new_words: A list of strings representing the new words to be spliced into the reference words.

    Yields:
        Word: A generator that yields Word objects distributed by syllables within the time
        ranges of the reference words.
    """

    word_map: Dict[Word, List[Word]] = {
        reference_word: [] for reference_word in reference_words
    }

    total_length = len(new_words)

    for i, word in enumerate(new_words):
        index = int(i / total_length * len(reference_words))
        reference_word = reference_words[index]

        word_map[reference_word].append(
            Word(
                text=word,
                timestamp=TimestampRange(
                    start=reference_word.timestamp.start,
                    end=reference_word.timestamp.end,
                ),
            )
        )

    for reference_word, words in word_map.items():
        yield from Word.distribute_words_by_syllables(
            words,
            start=reference_word.timestamp.start,
            end=reference_word.timestamp.end,
        )


def splice_by_syllables(
    reference_words: List[Word],
    new_words: List[str],
):
    """
    Splices a list of new words into reference words by syllables.

    This function maps each new word to a reference word, distributing them by syllables,
    and generates Word objects with timestamps matching those of the reference words.
    It then distributes these words by syllables within the time range of each reference word.

    Args:
        reference_words: A list of Word objects serving as reference for distribution.
        new_words: A list of strings representing the new words to be spliced into the reference words.

    Yields:
        Word: A generator that yields Word objects distributed by syllables within the time
        ranges of the reference words.
    """
    normalized = [
        *Word.distribute_by_syllables(
            words=[word for word in new_words],
            start=reference_words[0].timestamp.start,
            end=reference_words[-1].timestamp.end,
        )
    ]

    word_map: Dict[Word, List[Word]] = {
        reference_word: [] for reference_word in reference_words
    }

    for word in normalized:
        nearest_reference_word, _ = max(
            word_map.items(),
            key=lambda map: map[0].timestamp.get_intersection_percent(
                word.timestamp,
            )
            * map[0].syllables_count
            / (sum(word.syllables_count for word in map[1]) * 2 + 1),
        )

        word_map[nearest_reference_word].append(word)

    for reference_word, words in word_map.items():
        yield from Word.distribute_words_by_syllables(
            words,
            start=reference_word.timestamp.start,
            end=reference_word.timestamp.end,
        )
