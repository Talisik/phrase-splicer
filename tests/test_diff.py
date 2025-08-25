import unittest
from typing import List

from src.phrase_splicer.models.diff import Diff
from src.phrase_splicer.models.word import Word


class TestDiff(unittest.TestCase):
    """Test cases for the Diff class and its methods."""

    def _check_no_overlapping_timestamps(
        self,
        calibrated_diffs: List[Diff],
    ):
        """Helper method to check that words don't have overlapping timestamps."""
        active_words = [diff for diff in calibrated_diffs if diff.type != "removed"]

        # Check that each word has valid timestamp range
        for diff in active_words:
            self.assertLess(
                diff.word.timestamp.start.milliseconds,
                diff.word.timestamp.end.milliseconds,
                f"Word '{diff.word.text}' has invalid timestamp range",
            )

        # Check for overlapping timestamps between consecutive words
        for i in range(len(active_words) - 1):
            current_word = active_words[i]
            next_word = active_words[i + 1]
            self.assertLessEqual(
                current_word.word.timestamp.end.milliseconds,
                next_word.word.timestamp.start.milliseconds,
                f"Words '{current_word.word.text}' and '{next_word.word.text}' have overlapping timestamps",
            )

    def _verify(self, original: List[Word], new: List[Word]):
        diffs = list(Diff.compare(original, new))

        print("\nNon-calibrated diffs:")

        for diff in diffs:
            print(diff)

        calibrated = Diff.calibrate(diffs)

        print("\nCalibrated diffs:")

        for diff in calibrated:
            print(diff)

        self._check_no_overlapping_timestamps(calibrated)

    def test_word_removal(self):
        """Test removing words from a sequence."""
        self._verify(
            [
                Word.new("Hello", 0, 250),
                Word.new("World", 250, 1000),
            ],
            [
                Word.new("Hello", 0, 0),
            ],
        )

    def test_word_squeeze(self):
        """Test squeezing additional words into existing sequence."""
        self._verify(
            [
                Word.new("Hello", 0, 250),
                Word.new("World", 250, 1000),
            ],
            [
                Word.new("Hello", 0, 0),
                Word.new("Beautiful", 0, 0),
                Word.new("World", 0, 0),
            ],
        )

    def test_word_addition_middle(self):
        """Test adding a word in the middle of a sequence."""
        self._verify(
            [
                Word.new("The", 0, 250),
                Word.new("Great", 250, 500),
                Word.new("Gatsby", 750, 1000),
            ],
            [
                Word.new("The", 0, 0),
                Word.new("Great", 0, 0),
                Word.new("Silly", 0, 0),
                Word.new("Gatsby", 0, 0),
            ],
        )

    def test_word_addition_long_word(self):
        """Test adding a very long word (many syllables)."""
        self._verify(
            [
                Word.new("The", 0, 250),
                Word.new("Great", 250, 500),
                Word.new("Gatsby", 750, 1000),
            ],
            [
                Word.new("The", 0, 0),
                Word.new("Great", 0, 0),
                Word.new("Supercalifragilisticexpialidocious", 0, 0),
                Word.new("Gatsby", 0, 0),
            ],
        )

    def test_multiple_word_addition(self):
        """Test adding multiple words in sequence."""
        self._verify(
            [
                Word.new("The", 0, 250),
                Word.new("Great", 250, 500),
                Word.new("Gatsby", 750, 1000),
            ],
            [
                Word.new("The", 0, 0),
                Word.new("Great", 0, 0),
                Word.new("And", 0, 0),
                Word.new("Silly", 0, 0),
                Word.new("Wonderful", 0, 0),
                Word.new("Gatsby", 0, 0),
            ],
        )

    def test_left_addition(self):
        """Test adding a word at the beginning of a sequence."""
        self._verify(
            [
                Word.new("Great", 0, 500),
                Word.new("Gatsby", 500, 1000),
            ],
            [
                Word.new("The", 0, 0),
                Word.new("Great", 0, 0),
                Word.new("Gatsby", 0, 0),
            ],
        )

    def test_right_addition(self):
        """Test adding a word at the end of a sequence."""
        self._verify(
            [
                Word.new("The", 0, 500),
                Word.new("Great", 500, 1000),
            ],
            [
                Word.new("The", 0, 0),
                Word.new("Great", 0, 0),
                Word.new("Gatsby", 0, 0),
            ],
        )

    def test_word_replacement(self):
        """Test replacing a word with another word."""
        self._verify(
            [
                Word.new("The", 0, 200),
                Word.new("Big", 200, 400),
                Word.new("Brown", 400, 600),
                Word.new("Fox", 600, 800),
            ],
            [
                Word.new("The", 0, 0),
                Word.new("Big", 0, 0),
                Word.new("Red", 0, 0),
                Word.new("Fox", 0, 0),
            ],
        )


if __name__ == "__main__":
    unittest.main()
