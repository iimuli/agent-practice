from src.services.symptoms_service import SymptomsService
from src.exceptions import NoMatchingSymptomsError
from typing import Optional, List
from src.tools.dose_checker import check_medicine_dose_tool

service = SymptomsService(path="data/symptoms.json") #symptoms_checkerillä ajetaan tämä 

def check_symptoms_tool(
    symptoms: List[str],
    age_group: str,  # Lisätään potilastiedot tännekin hmm
    has_iv_access: bool = False,
    weight_kg: Optional[float] = None,
    is_elderly: bool = False
) -> str:
    """Kutsuu oiretarkastuksen ja ohjaa tuloksen perusteella eteenpäin."""
    try:

        meds: List[str] = service.determine_medicine_for_symptoms(symptoms)

        if len(meds) == 1: #!jos vain yksi lääke löytyy, palauta se patient datana
            return check_medicine_dose_tool(
                condition=symptoms[0], 
                age_group=age_group,
                has_iv_access=has_iv_access,
                weight_kg=weight_kg,
                is_elderly=is_elderly,
                preferred_medicine=meds[0]
            )
        else: #! useampi lääke löytynyt...
            med_options = ", ".join(meds)
            return (f"TARKENNUS TARVITAAN: Oirekuvaan soveltuu useampi lääkevaihtoehto: {med_options}. "
                    f"Kysy käyttäjältä mitä lääkettä käytetään, ja kutsu sen jälkeen lääkelaskuria.")

    except NoMatchingSymptomsError as e:
        return f"VIRHE/PUUTTUVA TIETO: {str(e)}"
    except Exception as e:
        return f"JÄRJESTELMÄVIRHE: Syötteiden käsittely epäonnistui ({str(e)})"