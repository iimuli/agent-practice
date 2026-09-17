from pydantic import BaseModel, Field, AliasChoices
from typing import List, Optional, Literal, Dict


class Symptoms(BaseModel):
    conditions: List[str]
    medicine: List[str]
