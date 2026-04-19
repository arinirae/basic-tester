from __future__ import annotations

import json
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from models.schemas import TestScenario
from services.playwright_service import detect_form_fields, run_test_scenario
from storage.memory_store import store
from utils.schema_value_generator import generate_values

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _parse_schema(schema_text: str) -> list:
    try:
        data = json.loads(schema_text or "[]")
        if isinstance(data, list):
            return data
        return []
    except json.JSONDecodeError:
        return []


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    scenarios = store.all()
    return templates.TemplateResponse("index.html", {"request": request, "scenarios": scenarios})


@router.get("/create", response_class=HTMLResponse)
def create_form(request: Request):
    return templates.TemplateResponse("create.html", {"request": request, "scenario": None, "errors": []})


@router.post("/create", response_class=HTMLResponse)
def create_submit(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    target_url: str = Form(...),
    schema_json: str = Form("[]"),
    requires_login: str = Form("none"),
    login_url: str = Form(""),
    login_username_field: str = Form(""),
    login_email_field: str = Form(""),
    login_password_field: str = Form(""),
    login_username: str = Form(""),
    login_email: str = Form(""),
    login_password: str = Form(""),
):
    errors = []
    parsed = _parse_schema(schema_json)
    if not title.strip():
        errors.append("Title is required.")
    if not target_url.strip():
        errors.append("Target URL is required.")
    if schema_json and parsed == []:
        errors.append("Schema JSON harus berupa array valid.")

    scenario = TestScenario(
        title=title.strip(),
        description=description.strip() or None,
        target_url=target_url.strip(),
        schema_json=schema_json.strip() or "[]",
        requires_login=requires_login,
        login_url=login_url.strip() or None,
        login_username_field=login_username_field.strip() or None,
        login_email_field=login_email_field.strip() or None,
        login_password_field=login_password_field.strip() or None,
        login_username=login_username.strip() or None,
        login_email=login_email.strip() or None,
        login_password=login_password.strip() or None,
    )

    if errors:
        return templates.TemplateResponse(
            "create.html",
            {"request": request, "scenario": scenario, "errors": errors},
        )

    store.add(scenario)
    return RedirectResponse(url="/", status_code=303)


@router.get("/edit/{scenario_id}", response_class=HTMLResponse)
def edit_form(request: Request, scenario_id: int):
    scenario = store.get(scenario_id)
    if not scenario:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("edit.html", {"request": request, "scenario": scenario, "errors": []})


@router.post("/edit/{scenario_id}", response_class=HTMLResponse)
def edit_submit(
    request: Request,
    scenario_id: int,
    title: str = Form(...),
    description: str = Form(""),
    target_url: str = Form(...),
    schema_json: str = Form("[]"),
    requires_login: str = Form("none"),
    login_url: str = Form(""),
    login_username_field: str = Form(""),
    login_email_field: str = Form(""),
    login_password_field: str = Form(""),
    login_username: str = Form(""),
    login_email: str = Form(""),
    login_password: str = Form(""),
):
    scenario = store.get(scenario_id)
    if not scenario:
        return RedirectResponse(url="/", status_code=303)

    errors = []
    parsed = _parse_schema(schema_json)
    if not title.strip():
        errors.append("Title is required.")
    if not target_url.strip():
        errors.append("Target URL is required.")
    if schema_json and parsed == []:
        errors.append("Schema JSON harus berupa array valid.")

    updated = TestScenario(
        id=scenario_id,
        title=title.strip(),
        description=description.strip() or None,
        target_url=target_url.strip(),
        schema_json=schema_json.strip() or "[]",
        requires_login=requires_login,
        login_url=login_url.strip() or None,
        login_username_field=login_username_field.strip() or None,
        login_email_field=login_email_field.strip() or None,
        login_password_field=login_password_field.strip() or None,
        login_username=login_username.strip() or None,
        login_email=login_email.strip() or None,
        login_password=login_password.strip() or None,
    )

    if errors:
        return templates.TemplateResponse(
            "edit.html",
            {"request": request, "scenario": updated, "errors": errors},
        )

    store.update(scenario_id, updated)
    return RedirectResponse(url="/", status_code=303)


@router.post("/delete/{scenario_id}")
def delete_scenario(scenario_id: int):
    store.delete(scenario_id)
    return RedirectResponse(url="/", status_code=303)


@router.get("/run/{scenario_id}", response_class=HTMLResponse)
def run_page(request: Request, scenario_id: int):
    scenario = store.get(scenario_id)
    if not scenario:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        "run.html",
        {"request": request, "scenario": scenario, "result": None},
    )


@router.post("/run/{scenario_id}", response_class=HTMLResponse)
async def run_submit(request: Request, scenario_id: int, values_json: str = Form("[]")):
    scenario = store.get(scenario_id)
    if not scenario:
        return RedirectResponse(url="/", status_code=303)

    try:
        values = json.loads(values_json or "[]")
        if isinstance(values, list):
            values = {item["name"]: item["value"] for item in values if item.get("name")}
    except json.JSONDecodeError:
        values = {}

    login_config = None
    if scenario.requires_login != "none":
        login_config = {
            "login_url": scenario.login_url,
            "login_username_field": scenario.login_username_field,
            "login_email_field": scenario.login_email_field,
            "login_password_field": scenario.login_password_field,
            "login_username": scenario.login_username,
            "login_email": scenario.login_email,
            "login_password": scenario.login_password,
        }

    result = {"status": "error", "message": "Tidak dapat menjalankan test."}
    try:
        result = await run_test_scenario(
            target_url=scenario.target_url,
            values=values,
            scenario_id=scenario_id,
            login_config=login_config,
        )
    except Exception as exc:
        result = {"status": "error", "message": str(exc)}

    return templates.TemplateResponse(
        "run.html",
        {"request": request, "scenario": scenario, "result": result},
    )


@router.post("/api/generate-values")
def api_generate_values(payload: dict):
    fields = payload.get("fields", [])
    values = generate_values(fields)
    return JSONResponse({"values": values})


@router.post("/api/detect-fields")
async def api_detect_fields(payload: dict):
    url = payload.get("url")
    if not url:
        return JSONResponse({"error": "URL is required."}, status_code=400)
    try:
        fields = await detect_form_fields(url)
        return JSONResponse({"fields": fields})
    except Exception as exc:
        import logging
        logging.error(f"API detect-fields error: {exc}")
        return JSONResponse({"error": str(exc)}, status_code=500)
