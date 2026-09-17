from src.services.dosing_service import DosingService
from src.models.medicine import PatientInput
from src.exceptions import DosingError
from typing import Optional

service = DosingService(data_path="data/medicines_v1.json") #luodaan palveluolio käynnistyessä, ei tarvitse aina lukea JSON tiedostoa uudelleen joka haulla

def format_dose_result(result: dict) -> str:
    """Yhteneväinen muotoilufunktio lääkeohjeen tulostamiseen."""
    route_str = ", ".join(result["route"]) if isinstance(result["route"], list) else result["route"]
    
    lines = [
        f"**Lääke:** {str(result['medicine']).capitalize()}",
        f"**Antoreitti:** {route_str}",
        f"**Annos:** {result['dose']}"
    ]
    
    if result.get("interval"):
        lines.append(f"**Toistettavuus:** {result['interval']}")
    if result.get("notes"):
        lines.append(f"**Huomioitavaa:** {str(result['notes']).capitalize()}")
    if result.get("antidote"):
        lines.append(f"**Vastalääke:** {str(result['antidote']).capitalize()}")

    return "\n".join(lines)

def check_medicine_dose_tool(
    condition: str,
    age_group: str,
    has_iv_access: bool = False,
    weight_kg: Optional[float] = None,
    is_elderly: bool = False,
    preferred_medicine: Optional[str] = None
) -> str:
    """Kutsuu laskentapalvelua ja palauttaa muotoillun tekstin agentille."""
    try:
        patient = PatientInput(
            condition=condition,
            age_group=age_group,
            weight_kg=weight_kg,
            is_elderly=is_elderly,
            has_iv_access=has_iv_access,
            preferred_medicine=preferred_medicine
        )
        
        result = service.calculate_dose(patient)
        return format_dose_result(result)

    except DosingError as e:
        return f"VIRHE/PUUTTUVA TIETO: {str(e)}"
    except Exception as e:
        return f"JÄRJESTELMÄVIRHE: Syötteiden käsittely epäonnistui ({str(e)})"