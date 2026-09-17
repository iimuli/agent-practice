import json
from typing import List, Optional, Dict
from src.models.symptoms import Symptoms #itse luodut pylancet datan luettavuudeksi
from src.exceptions import NoMatchingSymptomsError



class SymptomsService:
    def __init__(self, path: str):
        self.symptoms: List[Symptoms] = self._load_data(path)

    def _load_data(self, path: str) -> Dict[str, Symptoms]:
        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        symptoms_list= []
        for item in raw_data:
            symptoms_list.append(Symptoms(**item))

        return symptoms_list

    #         [ #!pylance/olio malli datasta
#     Symptoms(
#         conditions=["kouristus", "status epilepticus", "levottomuus", "delirium", "ketamiinin sivuvaikutus"],
#         medicine=["midatsolaami", "levetirasetaami"]
#     ),
#     Symptoms(
#         conditions=["kuume", "kipu"],
#         medicine=["parasetamoli"]
#     )
# ]

    def determine_medicine_for_symptoms(self, symptoms: List[str]) -> List[str]:
        matching_medicines = []

        for sym in symptoms:
            sym_clean = sym.lower().strip()
            for entry in self.symptoms:

                if any(sym_clean in c.lower() for c in entry.conditions): #löytyykö esim osittaista mistään listalta, ei exaktia
                    matching_medicines.extend(entry.medicine) #extendi jatkaa listaa, kun taas append "lisää listan listaan"
                    break
                # if sym_clean in entry.conditions:  #!tämä etsii exaktin matchin, ei toimi
                #     matching_medicines.append(entry.medicine)
                #     break

        if not matching_medicines:
            raise NoMatchingSymptomsError("Annettua oirekuvaa ei löydy tietokannasta.")

        return list(dict.fromkeys(matching_medicines)) #!poistaa duplikaatit säilyttäen alkuperäisen järjestyksen


    

