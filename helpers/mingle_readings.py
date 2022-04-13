# Copyright: Ren Tatsumoto <tatsu at autistici.org>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import enum
from typing import Optional, NamedTuple, List


class SplitFurigana(NamedTuple):
    head: str
    reading: str
    suffix: str


class WordReading(NamedTuple):
    word: str
    reading: Optional[str]


class WordWrap(NamedTuple):
    before: str
    after: str


@enum.unique
class WordWrapMode(enum.Enum):
    div = WordWrap('<div>', '</div>')
    span = WordWrap('<span>', '</span>')
    none = WordWrap('', '')


def split_furigana(text: str) -> SplitFurigana:
    furigana_start, furigana_end = -1, -1
    for i, c in enumerate(text):
        if c == '[':
            furigana_start = i
        if c == ']':
            furigana_end = i
    if furigana_start == furigana_end or furigana_start < 0 or furigana_end < 0:
        return SplitFurigana(text, text, "")
    else:
        return SplitFurigana(text[:furigana_start], text[furigana_start + 1:furigana_end], text[furigana_end + 1:])


def word_reading(text: str) -> WordReading:
    word, reading = [], []
    for split in map(split_furigana, text.split()):
        word.append(split.head + split.suffix)
        reading.append(split.reading + split.suffix)
    word, reading = ''.join(word), ''.join(reading)
    return WordReading(word, reading) if word != reading else WordReading(text, None)


def pairs(seq: List):
    for previous, current in zip(seq, seq[1:]):
        yield previous, current


def mingle_readings(readings: List[str], *, sep: str = '', wrap: WordWrap = WordWrapMode.div.value) -> str:
    """ Takes several furigana notations, packs them into one, with readings separated by sep. """

    assert len(readings) > 1

    packs = []
    split = list(map(str.split, readings))

    if any(len(x) != len(y) for x, y in pairs(split)):
        return readings[0]

    for pack in zip(*split):
        split = split_furigana(pack[0])
        word, readings, suffix = split.head, {split.reading: None, }, split.suffix
        for split in map(split_furigana, pack[1:]):
            readings[split.reading] = None
        readings = sep.join(f"{wrap.before}{reading}{wrap.after}" for reading in readings)
        packs.append(f' {word}[{readings}]{suffix}' if readings != word else word)
    return ''.join(packs)


if __name__ == '__main__':
    print(split_furigana('故郷[こきょう]'))
    print(split_furigana('有[あ]り'))
    print(split_furigana('ひらがな'))
    print(word_reading('有[あ]り 得[う]る'))
    print(word_reading('有る'))
    print(mingle_readings([' 有[あ]り 得[う]る', ' 有[あ]り 得[え]る', ' 有[あ]り 得[え]る']))
    print(mingle_readings([' 故郷[こきょう]', ' 故郷[ふるさと]']))
    print(mingle_readings(['お 前[まえ]', 'お 前[めえ]']))
    print(mingle_readings([' 言[い]い 分[ぶん]', ' 言い分[いーぶん]']))
