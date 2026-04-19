from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers.test import router as test_router

app = FastAPI(title="BasicTester Python Edition")

app.mount("/results", StaticFiles(directory="test_results"), name="results")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.include_router(test_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
