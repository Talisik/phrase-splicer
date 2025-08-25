import difflib
from dataclasses import dataclass
from typing import Iterable, List, Literal, Sequence, Tuple

from .word import Word


@dataclass(frozen=True)
class Diff:
    index: int
    """
    The index of the word in the original list.
    """

    word: Word
    """
    The word being compared.
    """

    type: Literal["unchanged", "removed", "added", "uncalibrated"]
    """
    The type of change.
    - unchanged: The word is the same in both lists.
    - removed: The word is not in the original list.
    - added: The word is not in the new list.
    - uncalibrated: The word is in the new list, but the timestamp is not calibrated.
    """

    def __str__(self):
        prefix = (
            " "
            if self.type == "unchanged"
            else "+"
            if self.type == "added"
            else "-"
            if self.type == "removed"
            else "?"
        )

        return "{0} [{1}] {2} @ {3}: {4} - {5}".format(
            prefix,
            self.index,
            self.word.text,
            self.word.syllables_count,
            self.word.timestamp.start.milliseconds,
            self.word.timestamp.end.milliseconds,
        )

    @classmethod
    def get_neighboring_diff_indices(
        cls,
        diffs: Sequence["Diff"],
        min_index: int,
        max_index: int,
    ):
        """
        Get the neighboring diffs before min_index and after max_index.

        Returns:
            Tuple of (diff_before, diff_after) where each can be None if not found.
        """
        l_index = -1
        r_index = -1

        # Find word before min_index
        for i in range(min_index - 1, -1, -1):
            if diffs[i].type in (
                "unchanged",
                "added",
                "uncalibrated",
            ):
                l_index = i
                break

        # Find word after max_index
        for i in range(max_index + 1, len(diffs)):
            if diffs[i].type in (
                "unchanged",
                "added",
                "uncalibrated",
            ):
                r_index = i
                break

        return l_index, r_index

    @classmethod
    def get_uncalibrated_phrases(cls, diffs: Sequence["Diff"]):
        """
        Get all uncalibrated phrases in the diff sequence.
        """
        current_phrase: List[Tuple[int, "Diff"]] = []

        for i, diff in enumerate(diffs):
            if diff.type == "uncalibrated":
                current_phrase.append((i, diff))

            elif current_phrase:
                yield current_phrase

                current_phrase = []

        # Don't forget the last phrase if it ends with uncalibrated words
        if current_phrase:
            yield current_phrase

    @classmethod
    def __calibrate_left_neighbor(
        cls,
        diffs: List["Diff"],
        initial_space: int,
        syllables_count: int,
        neighbor_diff_index: int,
    ):
        calibrated_duration = cls.__calibrate_one_neighbor(
            diffs,
            initial_space,
            syllables_count,
            neighbor_diff_index,
        )
        neighbor_diff = diffs[neighbor_diff_index]

        end_timestamp = neighbor_diff.word.timestamp.end.milliseconds + initial_space

        diffs[neighbor_diff_index] = Diff(
            index=neighbor_diff_index,
            word=Word.new(
                neighbor_diff.word.text,
                neighbor_diff.word.timestamp.start.milliseconds,
                neighbor_diff.word.timestamp.start.milliseconds + calibrated_duration,
            ),
            type=neighbor_diff.type,
        )

        return diffs[neighbor_diff_index].word.timestamp.end.milliseconds, end_timestamp

    @classmethod
    def __calibrate_right_neighbor(
        cls,
        diffs: List["Diff"],
        initial_space: int,
        syllables_count: int,
        neighbor_diff_index: int,
    ):
        calibrated_duration = cls.__calibrate_one_neighbor(
            diffs,
            initial_space,
            syllables_count,
            neighbor_diff_index,
        )
        neighbor_diff = diffs[neighbor_diff_index]

        start_timestamp = (
            neighbor_diff.word.timestamp.start.milliseconds - initial_space
        )

        diffs[neighbor_diff_index] = Diff(
            index=neighbor_diff_index,
            word=Word.new(
                neighbor_diff.word.text,
                neighbor_diff.word.timestamp.end.milliseconds - calibrated_duration,
                neighbor_diff.word.timestamp.end.milliseconds,
            ),
            type=neighbor_diff.type,
        )

        return start_timestamp, diffs[
            neighbor_diff_index
        ].word.timestamp.start.milliseconds

    @classmethod
    def __calibrate_one_neighbor(
        cls,
        diffs: List["Diff"],
        initial_space: int,
        syllables_count: int,
        neighbor_diff_index: int,
    ):
        neighbor_diff = diffs[neighbor_diff_index]

        # Get the total number of syllables and the total duration.
        neighbor_syllables_count = neighbor_diff.word.syllables_count
        syllables_count_total = neighbor_syllables_count + syllables_count

        # Get the duration of the neighbor word.
        neighbor_duration = neighbor_diff.word.timestamp.duration
        new_word_duration = max(
            0,
            round(neighbor_duration * syllables_count / syllables_count_total)
            - initial_space,
        )
        uncalibrated_duration = neighbor_duration - new_word_duration

        # Get the distribution of the neighbor word.
        neighbor_distribution = neighbor_syllables_count / syllables_count_total

        # Get the calibrated duration of the neighbor word.
        neighbor_calibrated_duration = min(
            neighbor_duration,
            round(uncalibrated_duration * neighbor_distribution),
        )

        return neighbor_calibrated_duration

    @classmethod
    def __calibrate_two_neighbors(
        cls,
        diffs: List["Diff"],
        initial_space: int,
        syllables_count: int,
        l_diff_index: int,
        r_diff_index: int,
    ):
        l_diff = diffs[l_diff_index]
        r_diff = diffs[r_diff_index]

        # Get the total number of syllables and the total duration.
        l_syllables_count = l_diff.word.syllables_count
        r_syllables_count = r_diff.word.syllables_count
        syllables_count_total = l_syllables_count + r_syllables_count + syllables_count

        # Get the duration of the left, right, and new words.
        l_duration = l_diff.word.timestamp.duration
        r_duration = r_diff.word.timestamp.duration
        total_duration = l_duration + r_duration
        new_word_duration = max(
            0,
            round(total_duration * syllables_count / syllables_count_total)
            - initial_space,
        )
        uncalibrated_duration = total_duration - new_word_duration

        # Get the distribution of the left and right words.
        l_distribution = l_syllables_count / syllables_count_total
        l_distribution *= l_duration / total_duration

        r_distribution = r_syllables_count / syllables_count_total
        r_distribution *= r_duration / total_duration

        distribution_total = l_distribution + r_distribution

        # Normalize the distribution.
        l_distribution /= distribution_total
        r_distribution /= distribution_total

        # Get the calibrated duration of the left and right words.
        l_calibrated_duration = min(
            l_duration,
            round(uncalibrated_duration * l_distribution),
        )
        r_calibrated_duration = min(
            r_duration,
            round(uncalibrated_duration * r_distribution),
        )

        # Update the words.
        diffs[l_diff_index] = Diff(
            index=l_diff_index,
            word=Word.new(
                l_diff.word.text,
                l_diff.word.timestamp.start.milliseconds,
                l_diff.word.timestamp.start.milliseconds + l_calibrated_duration,
            ),
            type=l_diff.type,
        )
        diffs[r_diff_index] = Diff(
            index=r_diff_index,
            word=Word.new(
                r_diff.word.text,
                r_diff.word.timestamp.end.milliseconds - r_calibrated_duration,
                r_diff.word.timestamp.end.milliseconds,
            ),
            type=r_diff.type,
        )

        return (
            diffs[l_diff_index].word.timestamp.end.milliseconds,
            diffs[r_diff_index].word.timestamp.start.milliseconds,
        )

    @classmethod
    def borrow_space(
        cls,
        diffs: List["Diff"],
        initial_space: int,
        syllables_count: int,
        l_diff_index: int,
        r_diff_index: int,
    ):
        if l_diff_index == -1 and r_diff_index == -1:
            return 0, 0

        if l_diff_index != -1 and r_diff_index != -1:
            return cls.__calibrate_two_neighbors(
                diffs,
                initial_space,
                syllables_count,
                l_diff_index,
                r_diff_index,
            )

        if l_diff_index != -1:
            return cls.__calibrate_left_neighbor(
                diffs,
                initial_space,
                syllables_count,
                l_diff_index,
            )

        if r_diff_index != -1:
            return cls.__calibrate_right_neighbor(
                diffs,
                initial_space,
                syllables_count,
                r_diff_index,
            )

        return 0, 0

    @classmethod
    def __calibrate_apply(
        cls,
        diffs: List["Diff"],
        phrase: List[Tuple[int, "Diff"]],
        syllables_count: int,
        start: int,
        space: int,
    ):
        for i, diff in phrase:
            weight = diff.word.syllables_count / syllables_count
            duration = int(space * weight)
            end = start + duration

            diffs[i] = Diff(
                index=i,
                word=Word.new(
                    diff.word.text,
                    start,
                    end,
                ),
                type="added",
            )
            start = end

    @classmethod
    def calibrate(
        cls,
        diffs: List["Diff"],
        min_space_ms_threshold: int = 100,
        space_ms_per_syllable_threshold: int = 100,
    ):
        """
        Calibrate timestamps for uncalibrated words in the diff sequence.
        The provided `diffs` may be modified.
        """
        uncalibrated_phrases = cls.get_uncalibrated_phrases(diffs)

        for phrase in uncalibrated_phrases:
            l_diff_index, r_diff_index = cls.get_neighboring_diff_indices(
                diffs, phrase[0][0], phrase[-1][0]
            )
            l_word = diffs[l_diff_index].word if l_diff_index != -1 else None
            r_word = diffs[r_diff_index].word if r_diff_index != -1 else None

            space = (
                l_word.timestamp.get_distance(r_word.timestamp)
                if l_word and r_word
                else 0
            )

            syllables_count = sum(diff[1].word.syllables_count for diff in phrase)
            space_threshold = max(
                min_space_ms_threshold,
                syllables_count * space_ms_per_syllable_threshold,
            )

            if space < space_threshold:
                start, end = cls.borrow_space(
                    diffs,
                    space,
                    syllables_count,
                    l_diff_index,
                    r_diff_index,
                )
                space = end - start

            else:
                start = l_word.timestamp.end.milliseconds if l_word else 0

            cls.__calibrate_apply(
                diffs,
                phrase,
                syllables_count,
                start,
                space,
            )

        return diffs

    @classmethod
    def compare(
        cls,
        a: Iterable[Word],
        b: Iterable[Word],
    ):
        a_list = list(a)
        b_list = list(b)

        # First pass: collect all diffs to understand the structure
        a_idx = 0
        b_idx = 0
        removed_words: List[Word] = []
        result: List[Diff] = []

        for line in list(
            difflib.ndiff(
                [item.text for item in a_list],
                [item.text for item in b_list],
            )
        ):
            if line.startswith("  "):  # unchanged
                result.append(
                    Diff(
                        index=a_idx,
                        word=a_list[a_idx],
                        type="unchanged",
                    )
                )
                a_idx += 1
                b_idx += 1

            elif line.startswith("- "):  # removed from a
                word = a_list[a_idx]
                result.append(
                    Diff(
                        index=a_idx,
                        word=a_list[a_idx],
                        type="removed",
                    )
                )
                removed_words.append(word)
                a_idx += 1

            elif line.startswith("+ "):  # added from b
                word = b_list[b_idx]
                calibrated = False

                if removed_words:
                    removed_word = removed_words.pop(0)
                    word = Word.new(
                        word.text,
                        removed_word.timestamp.start.milliseconds,
                        removed_word.timestamp.end.milliseconds,
                    )
                    calibrated = True

                elif result:
                    pass

                result.append(
                    Diff(
                        index=b_idx,
                        word=word,
                        type="added" if calibrated else "uncalibrated",
                    )
                )
                b_idx += 1

            # Skip lines starting with '?' (diff markers)

        return result
