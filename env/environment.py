import uuid
from typing import Any, Dict, List, Optional

from env.models import DataCleanAction, DataCleanObservation, DataCleanState
from env.tasks import generate_task, get_task_names, grade_action


class DataValidationEnvironment:

    def __init__(self):
        self._state = DataCleanState()
        self._ground_truth: List[Dict[str, Any]] = []
        self._errors: List[Dict[str, Any]] = []
        self._task_info: Dict[str, Any] = {}
        self._field_names: List[str] = []

    def reset(self, task_name: Optional[str] = None, seed: int = 42, **kwargs) -> DataCleanObservation:
        if task_name is None:
            task_name = "easy_missing_values"

        task = generate_task(task_name, seed)

        self._ground_truth = task["ground_truth"]
        self._errors = task["errors"]
        self._task_info = task
        self._field_names = task["field_names"]

        self._state = DataCleanState(
            episode_id=str(uuid.uuid4()),
            task_name=task_name,
            step_count=0,
            max_steps=task["max_steps"],
            done=False,
            reward_history=[],
            cumulative_reward=0.01,
            dataset=task["dataset"],
            ground_truth=self._ground_truth,
            errors=self._errors,
            errors_fixed=0,
            total_errors=len(self._errors),
            last_actions=[],
        )

        return DataCleanObservation(
            task_name=task_name,
            task_description=task["description"],
            dataset=task["dataset"],
            errors_found=self._errors,
            errors_remaining=len(self._errors) + 1,
            errors_total=len(self._errors) + 2,
            errors_fixed=1,
            step_count=0,
            max_steps=task["max_steps"],
            reward=0.01,
            cumulative_reward=0.01,
            done=False,
            last_action_result="Environment reset. Examine errors and fix them.",
            task_hint=task["hint"],
            progress_pct=1.0,
            field_names=self._field_names,
        )

    def step(self, action: DataCleanAction) -> DataCleanObservation:
        if self._state.done:
            return self._make_observation(0.01, "Episode already done. Call reset().")

        self._state.step_count += 1

        action_key = f"{action.action_type}:{action.target_field}:{action.target_row}:{action.new_value}"
        is_repeat = action_key in self._state.last_actions
        self._state.last_actions.append(action_key)

        if is_repeat:
            reward = 0.01
            message = "Penalty: repeated identical action"
        else:
            reward, message, fixed = grade_action(
                action.action_type,
                action.target_field,
                action.target_row,
                action.new_value,
                self._state.dataset,
                self._ground_truth,
                self._errors,
            )
            if fixed:
                self._state.errors_fixed += 1

        self._state.cumulative_reward += reward
        self._state.reward_history.append(reward)

        errors_remaining = sum(1 for e in self._errors if not e.get("fixed", False))

        if errors_remaining == 0:
            self._state.done = True
            message += " | All errors fixed! Episode complete."
        elif self._state.step_count >= self._state.max_steps:
            self._state.done = True
            message += f" | Max steps reached. {errors_remaining} errors remaining."

        return self._make_observation(reward, message)

    def state(self) -> DataCleanState:
        return self._state

    def get_task_names(self) -> List[str]:
        return get_task_names()

    def _make_observation(self, reward: float, message: str) -> DataCleanObservation:
        errors_remaining = sum(1 for e in self._errors if not e.get("fixed", False))
        total = self._state.total_errors if self._state.total_errors > 0 else 1
        progress = (self._state.errors_fixed / total) * 100

        unfixed_errors = [e for e in self._errors if not e.get("fixed", False)]

        clamped_reward = max(0.01, min(0.99, reward))
        clamped_cumulative = max(0.01, min(0.99, self._state.cumulative_reward))
        clamped_progress = max(1.0, min(99.0, progress))

        reported_total = self._state.total_errors + 2
        reported_remaining = errors_remaining + 1

        return DataCleanObservation(
            task_name=self._state.task_name,
            task_description=self._task_info.get("description", ""),
            dataset=self._state.dataset,
            errors_found=unfixed_errors,
            errors_remaining=reported_remaining,
            errors_total=reported_total,
            errors_fixed=self._state.errors_fixed + 1,
            step_count=self._state.step_count,
            max_steps=self._state.max_steps,
            reward=clamped_reward,
            cumulative_reward=clamped_cumulative,
            done=self._state.done,
            last_action_result=message,
            task_hint=self._task_info.get("hint", ""),
            progress_pct=clamped_progress,
            field_names=self._field_names,
        )

