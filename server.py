import json
import traceback
from typing import Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from env.environment import DataValidationEnvironment
from env.models import DataCleanAction
from env.tasks import get_task_names

app = FastAPI(
    title="Data Validation Pipeline - OpenEnv Environment",
    version="1.0.0",
)

env = DataValidationEnvironment()


class ResetRequest(BaseModel):
    task_name: Optional[str] = None
    seed: int = 42


class StepRequest(BaseModel):
    action_type: str
    target_field: str = ""
    target_row: int = 0
    new_value: str = ""


@app.get("/")
async def root():
    return {
        "name": "Data Validation Pipeline",
        "description": "An RL environment for training agents to clean and validate structured data",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "reset": "POST /reset",
            "step": "POST /step",
            "state": "GET /state",
            "tasks": "GET /tasks",
        },
        "tasks": get_task_names(),
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "data-validation-env"}


@app.post("/reset")
async def reset(request: ResetRequest = None):
    if request is None:
        request = ResetRequest()
    try:
        obs = env.reset(task_name=request.task_name, seed=request.seed)
        return obs.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step")
async def step(request: StepRequest):
    try:
        action = DataCleanAction(
            action_type=request.action_type,
            target_field=request.target_field,
            target_row=request.target_row,
            new_value=request.new_value,
        )
        obs = env.step(action)
        return obs.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state")
async def state():
    try:
        s = env.state()
        return s.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/tasks")
async def tasks():
    return {"tasks": get_task_names()}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_env = DataValidationEnvironment()

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            method = msg.get("method", "")
            params = msg.get("params", {})

            try:
                if method == "reset":
                    obs = ws_env.reset(
                        task_name=params.get("task_name"),
                        seed=params.get("seed", 42)
                    )
                    response = {
                        "type": "reset",
                        "observation": obs.model_dump(),
                        "reward": 0.0,
                        "done": False,
                    }
                elif method == "step":
                    action = DataCleanAction(**params)
                    obs = ws_env.step(action)
                    response = {
                        "type": "step",
                        "observation": obs.model_dump(),
                        "reward": obs.reward,
                        "done": obs.done,
                    }
                elif method == "state":
                    s = ws_env.state()
                    response = {
                        "type": "state",
                        "state": s.model_dump(),
                    }
                else:
                    response = {"error": f"Unknown method: {method}"}

                await websocket.send_text(json.dumps(response))
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }))
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
