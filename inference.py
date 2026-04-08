import json
import os
import re
import sys
import time
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN,
)

ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:8000")

TASKS = [
    {"task_name": "easy_missing_values", "seed": 42},
    {"task_name": "medium_mixed_errors", "seed": 42},
    {"task_name": "hard_multi_constraint", "seed": 42},
]

BENCHMARK_NAME = "data_validation_env"


def call_llm(messages: list) -> str:
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.0,
            max_tokens=1024,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return json.dumps({
            "action_type": "skip",
            "target_field": "",
            "target_row": 0,
            "new_value": ""
        })


def env_reset(task_name: str, seed: int = 42) -> dict:
    resp = requests.post(
        f"{ENV_BASE_URL}/reset",
        json={"task_name": task_name, "seed": seed},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def env_step(action: dict) -> dict:
    resp = requests.post(
        f"{ENV_BASE_URL}/step",
        json={"action": action},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def build_system_prompt(obs: dict) -> str:
    return f"""You are a data validation agent. Your task is to fix errors in a dataset.

TASK: {obs.get('task_description', '')}

AVAILABLE ACTIONS:
- fix_missing: Fix a missing/empty value
- fix_type: Fix a wrong data type (e.g., string "999.99" should be float 999.99)
- fix_range: Fix an out-of-range value (e.g., negative price)
- fix_format: Fix a format violation (e.g., wrong date format, invalid enum)
- fix_duplicate: Fix a duplicate entry
- validate: Check progress
- skip: Skip (no action)

You MUST respond with ONLY valid JSON in this exact format:
{{"action_type": "<type>", "target_field": "<field>", "target_row": <row_int>, "new_value": "<value>"}}

RULES:
1. Look at the errors_found list to identify what needs fixing
2. Use the correct action_type matching the error_type
3. For new_value, provide the CORRECT value (not the current wrong value)
4. The new_value must always be a string representation of the correct value
5. Respond with ONLY the JSON object, no explanation"""


def build_user_prompt(obs: dict) -> str:
    errors = obs.get("errors_found", [])
    dataset = obs.get("dataset", [])
    errors_text = json.dumps(errors, indent=2) if errors else "No errors remaining!"
    dataset_compact = []
    for i, row in enumerate(dataset):
        dataset_compact.append(f"Row {i}: {json.dumps(row)}")
    dataset_text = "\n".join(dataset_compact)

    return f"""CURRENT STATE:
- Step: {obs.get('step_count', 0)}/{obs.get('max_steps', 20)}
- Errors remaining: {obs.get('errors_remaining', 0)}/{obs.get('errors_total', 0)}
- Progress: {obs.get('progress_pct', 0):.1f}%
- Last result: {obs.get('last_action_result', '')}

HINT: {obs.get('task_hint', '')}

ERRORS TO FIX:
{errors_text}

DATASET:
{dataset_text}

Respond with ONLY a JSON action object to fix the next error."""


def parse_llm_response(response: str) -> dict:
    try:
        action = json.loads(response)
        return {
            "action_type": str(action.get("action_type", "skip")),
            "target_field": str(action.get("target_field", "")),
            "target_row": int(action.get("target_row", 0)),
            "new_value": str(action.get("new_value", "")),
        }
    except json.JSONDecodeError:
        pass

    json_match = re.search(r'\{[^}]+\}', response)
    if json_match:
        try:
            action = json.loads(json_match.group())
            return {
                "action_type": str(action.get("action_type", "skip")),
                "target_field": str(action.get("target_field", "")),
                "target_row": int(action.get("target_row", 0)),
                "new_value": str(action.get("new_value", "")),
            }
        except (json.JSONDecodeError, ValueError):
            pass

    return {"action_type": "skip", "target_field": "", "target_row": 0, "new_value": ""}


def run_episode(task_config: dict) -> None:
    task_name = task_config["task_name"]
    seed = task_config.get("seed", 42)
    rewards = []
    steps = 0
    success = False

    print(f"[START] task={task_name} env={BENCHMARK_NAME} model={MODEL_NAME}")

    try:
        raw = env_reset(task_name, seed)
        # Handle wrapped format: {"observation": {...}, "reward": ..., "done": ...}
        if "observation" in raw:
            obs = raw["observation"]
            obs["reward"] = raw.get("reward", obs.get("reward", 0.01))
            obs["done"] = raw.get("done", obs.get("done", False))
        else:
            obs = raw

        max_steps = obs.get("max_steps", 20)

        messages = [
            {"role": "system", "content": build_system_prompt(obs)},
        ]

        while not obs.get("done", False) and steps < max_steps:
            user_msg = build_user_prompt(obs)
            messages_for_call = messages + [{"role": "user", "content": user_msg}]

            llm_response = call_llm(messages_for_call)

            action = parse_llm_response(llm_response)
            action_str = json.dumps(action)

            error_msg = None
            try:
                raw = env_step(action)
                # Handle wrapped format
                if "observation" in raw:
                    obs = raw["observation"]
                    obs["reward"] = raw.get("reward", obs.get("reward", 0.01))
                    obs["done"] = raw.get("done", obs.get("done", False))
                else:
                    obs = raw
                reward = obs.get("reward", 0.01)
                done = obs.get("done", False)
            except Exception as e:
                error_msg = str(e)
                reward = 0.01
                done = False

            steps += 1
            reward = max(0.01, min(0.99, reward))
            rewards.append(reward)

            print(f"[STEP] step={steps} action={action_str} reward={reward:.2f} done={str(done).lower()} error={error_msg if error_msg else 'null'}")

            if done:
                break

        total_reward = sum(rewards)
        success = total_reward > 0.5

    except Exception as e:
        error_str = str(e)
        if steps == 0:
            print(f"[STEP] step=1 action=null reward=0.01 done=true error={error_str}")
            steps = 1
            rewards = [0.01]
    finally:
        rewards_str = ",".join(f"{r:.2f}" for r in rewards) if rewards else "0.01"
        print(f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}")


def main():
    for task_config in TASKS:
        run_episode(task_config)
        time.sleep(1)


if __name__ == "__main__":
    main()
