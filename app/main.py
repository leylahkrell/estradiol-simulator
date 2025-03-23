from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import numpy as np
from app.pharmacokinetics import calculate_multiple_doses
from app.pharmacokinetics import calculate_rate_constants, generate_menstrual_reference

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class EstradiolRequest(BaseModel):
    estradiol_type: str
    concentration: float
    dose: float
    frequency: float
    days: int
    body_weight: float
    initial_state: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/update-plot")
async def calculate_estradiol(data: EstradiolRequest):
    k_absorption, k_elimination = calculate_rate_constants(data.estradiol_type)
    time_days, levels_pg_ml = calculate_multiple_doses(
        data.concentration, data.dose, data.frequency, data.days,
        k_absorption, k_elimination, data.body_weight,
        data.estradiol_type, initial_state=data.initial_state
    )
    max_level = np.max(levels_pg_ml)
    min_level = np.min(levels_pg_ml[time_days >= data.frequency])
    ref_days, ref_e2 = generate_menstrual_reference(data.days)

    return {
        "time_days": time_days.tolist(),
        "levels_pg_ml": levels_pg_ml.tolist(),
        "max_level": max_level,
        "min_level": min_level,
        "ref_days": ref_days.tolist(),
        "ref_e2": ref_e2.tolist(),
    }
