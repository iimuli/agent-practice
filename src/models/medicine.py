from pydantic import BaseModel, Field, AliasChoices
from typing import List, Optional, Literal

class DoseRule(BaseModel):
    conditions: List[str]
    route: List[str] = Field(validation_alias=AliasChoices('route', 'routes'))
    requires_iv: bool
    dose: str
    interval: Optional[str] = None
    is_elderly: Optional[bool] = None
    max_single_dose: Optional[str] = None
    notes: Optional[str] = None

class AgeGroupRules(BaseModel):
    rules: List[DoseRule]

class Medicine(BaseModel):
    medicine: str
    antidote: Optional[str] = None
    route: Optional[List[str]] = Field(default=None, validation_alias=AliasChoices('route', 'routes'))
    adult: Optional[AgeGroupRules] = None
    child: Optional[AgeGroupRules] = None

class PatientInput(BaseModel):
    condition: str
    age_group: Literal["adult", "child"]
    weight_kg: Optional[float] = Field(default=None, gt=0, lt=150)
    is_elderly: bool = False
    has_iv_access: bool = False
    preferred_medicine: Optional[str] = None