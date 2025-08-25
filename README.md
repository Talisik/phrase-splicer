# Phrase Splicer

A Python library for manipulating and splicing phrases with precise timing control. This library is particularly useful for applications involving speech processing, subtitle generation, and audio-text alignment.

## Features

-   **Timestamp Management**: Precise control over word and phrase timing
-   **Pause Detection**: Identify pauses between words in a sequence
-   **Flexible Splicing**: Splice new words into existing phrases with timing preservation
-   **Multiple Splicing Strategies**:
    -   Even distribution (`splice_evenly`)
    -   Syllable-based distribution (`splice_by_syllables`)
-   **Advanced Word Comparison**: Compare word sequences and identify differences with the `Diff` class
-   **Intelligent Timestamp Calibration**: Automatically calibrate timestamps for new words based on neighboring words and syllable counts
-   **Enhanced Word Distribution**: Multiple distribution methods including character-based and syllable-based distribution
-   **Syllable-Aware Processing**: Automatic syllable counting for more accurate timing distribution
-   **Language Support**: Works with multiple languages including English and Japanese
-   **Text Romanization**: Convert text from various languages to romanized form

## Installation

```bash
pip install git+https://github.com/Talisik/phrase-splicer.git
```

## Requirements

-   Python 3.10+
-   pykakasi 2.x (for Japanese language support)
-   syllables 1.x (for syllable counting)
-   uroman 1.x (for romanization of various languages)
-   fun-things 0.48.x

## Usage

### Basic Example

```python
from phrase_splicer import Word, Timestamp, TimestampRange, splice_evenly, splice_by_syllables, Diff

# Create words with timestamps
words = [
    Word(text="Hello", timestamp=TimestampRange(
        start=Timestamp(milliseconds=0),
        end=Timestamp(milliseconds=500)
    )),
    Word(text="world", timestamp=TimestampRange(
        start=Timestamp(milliseconds=600),
        end=Timestamp(milliseconds=1000)
    ))
]

# Splice new words evenly
new_words = ["Goodbye", "cruel", "world"]
result = splice_evenly(words, new_words)

# Splice new words based on syllable count
syllable_result = splice_by_syllables(words, new_words)
```

### Finding Pauses

```python
from phrase_splicer import Word, Timestamp, TimestampRange, get_pauses

words = [
    Word(text="Hello", timestamp=TimestampRange(
        start=Timestamp(milliseconds=0),
        end=Timestamp(milliseconds=500)
    )),
    Word(text="world", timestamp=TimestampRange(
        start=Timestamp(milliseconds=600),
        end=Timestamp(milliseconds=1000)
    ))
]

pauses = list(get_pauses(words))
# Returns a TimestampRange for the pause between "Hello" and "world"
```

### Text Romanization

```python
from phrase_splicer import romanize

# Romanize Japanese text
japanese_text = "こんにちは世界"
romanized_jp = romanize(japanese_text)

# Romanize text in other languages
other_text = "Привет мир"  # Russian
romanized_other = romanize(other_text)
```

### Word Comparison and Diff

```python
from phrase_splicer import Word, Timestamp, TimestampRange, Diff

# Original words with timestamps
original_words = [
    Word.new("Hello", 0, 500),
    Word.new("world", 600, 1000),
]

# New words (timestamps will be calibrated automatically)
new_words = [
    Word.new("Hello", 0, 0),
    Word.new("beautiful", 0, 0),  # New word to be inserted
    Word.new("world", 0, 0),
]

# Compare the word sequences
diffs = Diff.compare(original_words, new_words)

# Print the differences
for diff in diffs:
    print(diff)

# Calibrate timestamps for uncalibrated words
calibrated_diffs = Diff.calibrate(diffs)

# Extract the final word sequence with proper timestamps
final_words = [diff.word for diff in calibrated_diffs if diff.type != "removed"]
```

### Enhanced Word Distribution

```python
from phrase_splicer import Word, Timestamp

# Distribute words by syllables
words = ["Hello", "beautiful", "world"]
distributed_words = list(Word.distribute_by_syllables(
    words,
    start=Timestamp(0),
    end=Timestamp(2000)
))

# Distribute words by character count
char_distributed = list(Word.distribute_by_characters(
    words,
    start=Timestamp(0),
    end=Timestamp(2000)
))

# Each word gets timing proportional to its syllable count or character count
for word in distributed_words:
    print(f"{word.text}: {word.timestamp.start.milliseconds}-{word.timestamp.end.milliseconds}ms")
```

## API Reference

### Core Classes

-   `Word`: Represents a word with text and timestamp information
    -   `syllables_count`: Property that returns the estimated syllable count
    -   `new(text, start_ms, end_ms)`: Class method to create a word with millisecond timestamps
    -   `distribute_by_syllables(words, start, end)`: Distribute words by syllable count
    -   `distribute_by_characters(words, start, end)`: Distribute words by character count
    -   `distribute_words_by_syllables(words, start, end)`: Distribute existing Word objects by syllables
-   `TimestampRange`: Represents a time range with start and end timestamps
    -   `duration`: Property that returns the duration in milliseconds
    -   `get_distance(other)`: Returns distance between two timestamp ranges
    -   `get_intersection_duration(other)`: Returns overlap duration with another range
    -   `get_intersection_percent(other)`: Returns overlap as percentage of total duration
-   `Timestamp`: Represents a single point in time
-   `Diff`: Represents a difference between two word sequences
    -   `compare(a, b)`: Class method to compare two word sequences
    -   `calibrate(diffs)`: Class method to calibrate timestamps for uncalibrated words
    -   `get_uncalibrated_phrases(diffs)`: Get sequences of uncalibrated words
    -   `borrow_space(diffs, space, syllables, left_idx, right_idx)`: Borrow timing from neighboring words
-   `Item`: Simple data class with text and weight properties

### Main Functions

-   `splice_evenly`: Distributes new words evenly across the timing of reference words
-   `splice_by_syllables`: Distributes new words based on syllable count
-   `get_pauses`: Identifies pauses between words
-   `romanize`: Converts text from various languages to romanized form

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/Talisik/phrase-splicer.git
cd phrase-splicer

# Install development dependencies
pip install -r requirements.txt
```

### Project Structure

```
phrase-splicer/
├── src/
│   └── phrase_splicer/
│       ├── models/
│       │   ├── diff.py
│       │   ├── item.py
│       │   ├── timestamp.py
│       │   ├── timestamp_range.py
│       │   └── word.py
│       ├── __init__.py
│       ├── constants.py
│       └── utils.py
├── tests/
│   └── test_diff.py
├── pyproject.toml
├── setup.cfg
├── setup.py
└── requirements.txt
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
