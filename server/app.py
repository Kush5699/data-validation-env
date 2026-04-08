"""
FastAPI application for the Data Validation Environment.

Uses openenv's create_app() for standard-compliant API endpoints.
"""

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError(
        "openenv-core is required. Install with: pip install openenv-core"
    ) from e

from env.models import DataCleanAction, DataCleanObservation
from env.environment import DataValidationEnvironment

# Create the app using the official openenv framework
app = create_app(
    DataValidationEnvironment,
    DataCleanAction,
    DataCleanObservation,
    env_name="data_validation_env",
    max_concurrent_envs=1,
)


def main(host: str = "0.0.0.0", port: int = 8000):
    """Run the Data Validation environment server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
