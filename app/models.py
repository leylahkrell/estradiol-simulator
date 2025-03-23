from pydantic import BaseModel

class EstradiolSimulationRequest(BaseModel):
    estradiol_type: str
    concentration: float
    dose: float
    frequency: float
    days: int
    body_weight: float
    initial_state: str
    show_reference: bool

class EstradiolSimulationResponse(BaseModel):
    time_days: list
    levels_pg_ml: list
    max_level: float
    min_level: float
    plot_url: str