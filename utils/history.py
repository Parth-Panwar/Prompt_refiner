from dataclasses import dataclass, field
from datetime import datetime
from core.refiner import RefinementResult


@dataclass
class HistoryEntry:
    result: RefinementResult
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def label(self) -> str:
        preview = self.result.raw_input[:60]
        if len(self.result.raw_input) > 60:
            preview += "..."
        return f"{self.timestamp.strftime('%H:%M')} — {preview}"


class HistoryManager:
    def __init__(self, max_entries: int = 10):
        self.max_entries = max_entries
        self._entries: list[HistoryEntry] = []

    def add(self, result: RefinementResult) -> None:
        self._entries.insert(0, HistoryEntry(result=result))
        if len(self._entries) > self.max_entries:
            self._entries.pop()

    def get_all(self) -> list[HistoryEntry]:
        return self._entries

    def clear(self) -> None:
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)