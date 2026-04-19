from __future__ import annotations

import json
from typing import Dict, List, Optional

from models.schemas import TestScenario


class MemoryStore:
    def __init__(self) -> None:
        self._store: Dict[int, TestScenario] = {}
        self._next_id = 1
        self._seed_example()

    def _seed_example(self) -> None:
        example = TestScenario(
            id=self._next_id,
            title="Contoh Form Pendaftaran",
            description="Form contoh dengan email, nama, dan nomor telepon.",
            target_url="https://example.com",
            schema_json=json.dumps([
                {
                    "name": "email",
                    "label": "Email",
                    "type": "email",
                    "required": True,
                    "placeholder": "test@example.com"
                },
                {
                    "name": "name",
                    "label": "Nama Lengkap",
                    "type": "text",
                    "required": True,
                    "placeholder": "John Doe"
                },
                {
                    "name": "phone",
                    "label": "Telepon",
                    "type": "tel",
                    "placeholder": "+628123456789"
                }
            ], indent=2),
        )
        self._store[self._next_id] = example
        self._next_id += 1

    def all(self) -> List[TestScenario]:
        return list(self._store.values())

    def get(self, scenario_id: int) -> Optional[TestScenario]:
        return self._store.get(scenario_id)

    def add(self, scenario: TestScenario) -> TestScenario:
        scenario.id = self._next_id
        self._store[self._next_id] = scenario
        self._next_id += 1
        return scenario

    def update(self, scenario_id: int, scenario: TestScenario) -> Optional[TestScenario]:
        if scenario_id not in self._store:
            return None
        scenario.id = scenario_id
        self._store[scenario_id] = scenario
        return scenario

    def delete(self, scenario_id: int) -> bool:
        if scenario_id in self._store:
            del self._store[scenario_id]
            return True
        return False


store = MemoryStore()
