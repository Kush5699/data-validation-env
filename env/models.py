from typing import Any, Dict, List, Optional
from pydantic import Field

from openenv.core.env_server.types import Action, Observation, State


class DataCleanAction(Action):
    action_type: str = Field(...)
    target_field: str = Field(default="")
    target_row: int = Field(default=0)
    new_value: str = Field(default="")


class DataCleanObservation(Observation):
    task_name: str = Field(default="")
    task_description: str = Field(default="")
    dataset: List[Dict[str, Any]] = Field(default_factory=list)
    errors_found: List[Dict[str, Any]] = Field(default_factory=list)
    errors_remaining: int = Field(default=0)
    errors_total: int = Field(default=0)
    errors_fixed: int = Field(default=0)
    step_count: int = Field(default=0)
    max_steps: int = Field(default=20)
    cumulative_reward: float = Field(default=0.0)
    last_action_result: str = Field(default="")
    task_hint: str = Field(default="")
    available_actions: List[str] = Field(
        default_factory=lambda: [
            "fix_missing", "fix_type", "fix_range", "fix_format",
            "fix_duplicate", "validate", "skip"
        ]
    )
    progress_pct: float = Field(default=0.0)
    field_names: List[str] = Field(default_factory=list)


class DataCleanState(State):
    task_name: str = Field(default="")
    max_steps: int = Field(default=20)
    done: bool = Field(default=False)
    reward_history: List[float] = Field(default_factory=list)
    cumulative_reward: float = Field(default=0.0)
    dataset: List[Dict[str, Any]] = Field(default_factory=list)
    ground_truth: List[Dict[str, Any]] = Field(default_factory=list)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    errors_fixed: int = Field(default=0)
    total_errors: int = Field(default=0)
    last_actions: List[str] = Field(default_factory=list)
