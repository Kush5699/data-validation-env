---
title: Data Validation Pipeline
emoji: 🧹
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
tags:
  - openenv
---

# Data Validation Pipeline — OpenEnv Environment

An RL environment for training AI agents to clean and validate structured data. Built on the [OpenEnv](https://github.com/meta-pytorch/OpenEnv) framework for the Meta-PyTorch Hackathon.

## 🌐 Environment Overview

The **Data Validation Pipeline** environment simulates real-world data quality challenges. An agent is presented with a "dirty" dataset containing various errors — missing values, type mismatches, format violations, range errors, and duplicates — and must systematically identify and fix each issue.

### Motivation

Data quality is a critical challenge in every organization. Poor data leads to incorrect analytics, broken ML models, and costly business decisions. This environment trains RL agents to become automated data stewards, capable of:
- Detecting and classifying data errors
- Applying appropriate fixes
- Optimizing their correction strategy for efficiency

## 🎯 Action Space

The agent can take the following **discrete actions**:

| Action Type | Description | Parameters |
|-------------|-------------|------------|
| `fix_missing` | Fill in a missing/empty value | `target_row`, `target_field`, `new_value` |
| `fix_type` | Correct a data type error (e.g., string → float) | `target_row`, `target_field`, `new_value` |
| `fix_range` | Fix an out-of-range value | `target_row`, `target_field`, `new_value` |
| `fix_format` | Fix a format violation (e.g., date format) | `target_row`, `target_field`, `new_value` |
| `fix_duplicate` | Resolve a duplicate entry | `target_row`, `target_field`, `new_value` |
| `validate` | Check current progress | — |
| `skip` | Skip (no action) | — |

### Action JSON Schema
```json
{
  "action_type": "fix_missing|fix_type|fix_range|fix_format|fix_duplicate|validate|skip",
  "target_field": "column_name",
  "target_row": 0,
  "new_value": "corrected_value"
}
```

## 👁️ Observation Space

Each observation includes:

| Field | Type | Description |
|-------|------|-------------|
| `task_name` | string | Current task identifier |
| `task_description` | string | What needs to be done |
| `dataset` | list[dict] | Current state of the dataset |
| `errors_found` | list[dict] | Remaining errors with details |
| `errors_remaining` | int | Count of unfixed errors |
| `errors_total` | int | Total errors at start |
| `errors_fixed` | int | Successfully fixed errors |
| `step_count` | int | Current step number |
| `max_steps` | int | Step budget |
| `reward` | float | Reward from last action |
| `cumulative_reward` | float | Total reward so far |
| `done` | bool | Episode finished? |
| `last_action_result` | string | Feedback from last action |
| `task_hint` | string | Hint for solving the task |
| `progress_pct` | float | Completion percentage |
| `field_names` | list[str] | Dataset column names |

## 📋 Tasks

### Task 1: Easy — Missing Values (difficulty: ⭐)
- **Dataset**: 5-row employee table
- **Errors**: 3 missing values (empty strings)
- **Max Steps**: 10
- **Strategy**: Find empty fields and fill with correct values
- **Solvable in**: ≤5 steps

### Task 2: Medium — Mixed Errors (difficulty: ⭐⭐)
- **Dataset**: 7-row product inventory
- **Errors**: 6 errors (type, format, missing, range, duplicate)
- **Max Steps**: 15
- **Strategy**: Classify error type, match to correct action
- **Requires**: Type awareness + format rules

### Task 3: Hard — Multi-Constraint (difficulty: ⭐⭐⭐)
- **Dataset**: 10-row customer orders
- **Errors**: 10 interrelated errors across all types
- **Max Steps**: 20
- **Strategy**: Plan error resolution order, handle dependencies
- **Requires**: Domain knowledge + planning

## 🏗️ Setup & Usage

### Docker (Recommended)
```bash
docker build -t data-validation-env .
docker run -p 8000:8000 data-validation-env
```

### Local Development
```bash
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Reset with easy task
curl -X POST http://localhost:8000/reset \
  -H "Content-Type: application/json" \
  -d '{"task_name": "easy_missing_values", "seed": 42}'

# Take a step
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{"action_type": "fix_missing", "target_field": "email", "target_row": 1, "new_value": "bob@example.com"}'

# Check state
curl http://localhost:8000/state
```

### Run Inference Agent
```bash
export HF_TOKEN=your_token_here
export API_BASE_URL=https://api.openai.com/v1
export MODEL_NAME=gpt-4.1-mini
python inference.py
```

## 📊 Baseline Performance

| Task | Model | Avg Reward | Steps Used | Success Rate |
|------|-------|-----------|------------|-------------|
| easy_missing_values | gpt-4.1-mini | 0.85 | 4/10 | 90% |
| medium_mixed_errors | gpt-4.1-mini | 0.70 | 9/15 | 75% |
| hard_multi_constraint | gpt-4.1-mini | 0.55 | 15/20 | 50% |

## 🏆 Reward Design

- **Correct fix**: `+1.0 / total_errors` (proportional to error count)
- **Wrong value**: `-0.05` penalty
- **Wrong action type**: `-0.05` penalty
- **Repeated action**: `-0.1` penalty
- **Skip/Validate**: `0.0` (neutral)

The reward design encourages:
1. **Accuracy**: Correct fixes get proportional positive reward
2. **Efficiency**: Penalties for wrong attempts
3. **Exploration**: No penalty for validation checks
4. **Diversity**: Penalizes repeated identical actions

## 📁 Project Structure
```
├── inference.py          ← LLM agent loop
├── openenv.yaml          ← OpenEnv metadata
├── Dockerfile            ← Container config
├── requirements.txt      ← Python dependencies
├── server.py             ← FastAPI app
├── README.md             ← This file
└── env/
    ├── __init__.py
    ├── models.py          ← Pydantic models
    ├── tasks.py           ← Task registry & graders
    └── environment.py     ← Core environment
```

## 📜 License

BSD-3-Clause
