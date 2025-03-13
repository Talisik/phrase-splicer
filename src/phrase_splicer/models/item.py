from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    text: str
    weight: float
