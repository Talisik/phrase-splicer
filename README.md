# Phrase Splicer

A Python library for manipulating and splicing phrases with precise timing control. This library is particularly useful for applications involving speech processing, subtitle generation, and audio-text alignment.

## Features

-   **Timestamp Management**: Precise control over word and phrase timing
-   **Pause Detection**: Identify pauses between words in a sequence
-   **Flexible Splicing**: Splice new words into existing phrases with timing preservation
-   **Multiple Splicing Strategies**:
    -   Even distribution (`splice_evenly`)
    -   Syllable-based distribution (`splice_by_syllables`)
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
from phrase_splicer import Word, Timestamp, TimestampRange, splice_evenly, splice_by_syllables

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

## API Reference

### Core Classes

-   `Word`: Represents a word with text and timestamp information
-   `TimestampRange`: Represents a time range with start and end timestamps
-   `Timestamp`: Represents a single point in time

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
│       │   ├── timestamp.py
│       │   ├── timestamp_range.py
│       │   └── word.py
│       ├── __init__.py
│       ├── constants.py
│       └── utils.py
├── pyproject.toml
├── setup.cfg
├── setup.py
└── requirements.txt
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
