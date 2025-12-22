from __future__ import annotations

from typing import Protocol

class Pathlike[T](Protocol):
    def __fspath__(self) -> T:
        ...

type StrPath = str | Pathlike[str]
