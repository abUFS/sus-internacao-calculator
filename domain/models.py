from datetime import date
from pydantic import BaseModel
from typing import Optional

class Period(BaseModel):
    start: date
    end: date

class Procediment(BaseModel):
    code: str
    name: str
    avrg_stay: int

class CalcRequest(BaseModel):
    hospitalization: Period
    procediment: Procediment
    itu_periods: Optional[list[Period]] = []
