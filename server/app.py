"""
FastAPI application for the Data Validation Environment.

Uses a STATEFUL single environment instance so that /reset and /step share state.
Responses use the standard OpenEnv format: {observation, reward, done}.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional

from env.models import DataCleanAction, DataCleanObservation
from env.environment import DataValidationEnvironment


# ── Pydantic request / response models matching OpenEnv wire format ──────────

class ResetRequest(BaseModel):
    class Config:
        extra = "allow"
    task_name: Optional[str] = None
    seed: Optional[int] = 42
    episode_id: Optional[str] = None


class StepRequest(BaseModel):
    class Config:
        extra = "allow"
    action: Dict[str, Any]


class EnvResponse(BaseModel):
    observation: Dict[str, Any]
    reward: Optional[float] = None
    done: bool = False


# ── Shared environment instance (stateful across requests) ───────────────────

env = DataValidationEnvironment()


# ── FastAPI app ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="OpenEnv Environment HTTP API",
    version="1.0.0",
)


def _serialize_observation(obs: DataCleanObservation) -> EnvResponse:
    """Convert observation to OpenEnv standard response format."""
    obs_dict = obs.model_dump(exclude={"reward", "done", "metadata"})
    return EnvResponse(
        observation=obs_dict,
        reward=obs.reward,
        done=obs.done,
    )


# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/metadata")
def metadata():
    return {
        "name": "data_validation_env",
        "description": "An RL environment for training agents to clean and validate structured data.",
    }


@app.get("/schema")
def schema():
    return {
        "action": DataCleanAction.model_json_schema(),
        "observation": DataCleanObservation.model_json_schema(),
        "state": {},
    }


@app.get("/state")
def state():
    s = env.state
    return s.model_dump() if hasattr(s, "model_dump") else {"episode_id": None, "step_count": 0}


@app.post("/reset")
def reset(request: ResetRequest = ResetRequest()):
    obs = env.reset(
        task_name=request.task_name,
        seed=request.seed if request.seed is not None else 42,
        episode_id=request.episode_id,
    )
    return _serialize_observation(obs)


@app.post("/step")
def step(request: StepRequest):
    try:
        action = DataCleanAction.model_validate(request.action)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    obs = env.step(action)
    return _serialize_observation(obs)


# ── Entry point ──────────────────────────────────────────────────────────────

def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
