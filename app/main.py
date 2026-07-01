"""Application entrypoint — created in this step as a placeholder.

Real wiring (routers, middleware, lifespan/DB startup) will be added
incrementally as each feature lands, starting with the config & DB
session setup in the next step.
"""

from fastapi import FastAPI

app = FastAPI(
    title="PC Parts Store & Smart PC Builder",
    description="E-commerce backend with a rule-based Smart PC Builder.",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
