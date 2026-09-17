import json
from typing import List, Optional, Dict
from src.models.medicine import Medicine, PatientInput, DoseRule #itse luodut pylancet datan luettavuudeksi
from src.exceptions import DosingError, MissingPatientDataError, NoMatchingRuleError #itse luodut virhefunktiot

class DosingService:
    def __init__(self, data_path: str):
        self.medicines: Dict[str, Medicine] = self._load_data(data_path) #ajautuu kun koodi luodaan, ottaa polun lääkeelle (tai myöhemmin lääkkeille). Tallentuu muuttujaan self.medicines
# { #! rakenne kirjastossa
#     "midatsolaami": Medicine(
#         medicine="Midatsolaami",
#         antidote="Flumatseniili",
#         route=["iv", "im", "buccal"],
#         adult=RulesGroup(...),
#         child=RulesGroup(...)
#     ),
# }

# #! O(1) haku suoraan avaimen nimen perusteella
# med = self.medicines["midatsolaami"]

# print(med.antidote)  #! Palauttaa: "Flumatseniili"
# print(med.route[0])  #! Palauttaa: "iv"


    def _load_data(self, path: str) -> Dict[str, Medicine]:
        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        medicines = {}
        for med_name, med_data in raw_data.items():
            if isinstance(med_data, dict):
                # Asetetaan nimi jos puuttuu
                if "medicine" not in med_data:
                    med_data["medicine"] = med_name
                medicines[med_name.lower()] = Medicine(**med_data)
        return medicines

#     raw_data = { #!RAAKA DATA ENNEN PURKAMISTA
#     "midatsolaami": {
#         "antidote": "flumatseniili",
#         "route": ["i.v.", "i.n.", "bu.", "i.m."],
#         "adult": { ... }
#     }
# }

# Medicine( #! DATA PURKAMISEN JÄLKEEN **med_data
#     antidote="flumatseniili",
#     route=["i.v.", "i.n.", "bu.", "i.m."],
#     adult={ ... }
# )


# { #! JOLLOIN löytyy in self.medicines:
#     "midatsolaami": Medicine( 
#         antidote="flumatseniili",
#         route=["i.v.", "i.n.", "bu.", "i.m."],
#         adult=AgeGroupRules(
#             rules=[
#                 DoseRule(condition=["kouristus"], route=["i.v."], dose="2.5mg", ...),
#                 DoseRule(condition=["kouristus"], route=["i.n."], dose="5mg", ...)
#             ]
#         )
#     )
# }

    def calculate_dose(self, patient: PatientInput) -> dict:

        med_name = patient.preferred_medicine.lower()
        if med_name not in self.medicines: #lääkettä ei löydy tietokannasta....
            raise NoMatchingRuleError(f"Lääkettä '{med_name}' ei löydy tietokannasta.")

        med = self.medicines[med_name]

        if patient.age_group == "child" and patient.weight_kg is None: #jos lapsi, varmistetaan että paino löytyy datasta
            raise MissingPatientDataError("Lapsipotilaan paino (kg) on pakollinen tieto annoksen laskemiseksi.")

        rules_group = med.child if patient.age_group == "child" else med.adult #säännöksi joko aikusi tai lapsi potilaan ohjeet kyseisestä lääkkeestä
        if not rules_group: 
            raise NoMatchingRuleError(f"Ei ohjetta ikäryhmälle: {patient.age_group}.") #lääkkeelle ei olemassa dataa syystä tai toisesta

       
        matching_rules: List[DoseRule] = []  #katellaa sopivat säännöt
        for rule in rules_group.rules:
            if patient.condition.lower() not in [c.lower() for c in rule.conditions]: #   "condition": ["kouristus"], lääkeohjeessa
                continue
            if rule.requires_iv and not patient.has_iv_access:
                continue
            if patient.age_group == "adult" and rule.is_elderly is not None:
                if rule.is_elderly != patient.is_elderly:
                    continue
            matching_rules.append(rule)

        if not matching_rules:
            raise NoMatchingRuleError("Sopivaa antoreittiä tai annosteluohetta ei löytnyt annetuilla ehdoilla.")

       
        route_priority = med.route #ottaa arraysta järjestyksessä antoreitin, eli jos ei iv. yhteyttä, ehdottaa in. ensisijaisesti (lääkkeestä riippuen)
        matching_rules.sort(
            key=lambda r: route_priority.index(r.route) if r.route in route_priority else 99
        )  #järjestetään reittiprioriteetin mukaan

        selected_rule = matching_rules[0] #ottaa ensimmäisen ohjeen järjestellystä listasta

        # Lasketaan lapsen painoon perustuva annos tarvittaessa
        final_dose = selected_rule.dose
        if patient.age_group == "child" and "/kg" in selected_rule.dose and patient.weight_kg:
            import re
            match = re.search(r"[\d\.]+", selected_rule.dose)
            if match:
                dose_val = float(match.group()) * patient.weight_kg
                if selected_rule.max_single_dose:
                    max_match = re.search(r"[\d\.]+", selected_rule.max_single_dose)
                    if max_match:
                        dose_val = min(dose_val, float(max_match.group()))
                final_dose = f"{dose_val}mg"

        return{
            "medicine": med.medicine if hasattr(med, 'medicine') else med_name,
            "route": selected_rule.route,
            "dose": final_dose,
            "interval": selected_rule.interval,
            "notes": selected_rule.notes,
            "antidote": med.antidote
        }

#     class Medicine(BaseModel): #! vaikka antidote/notes ei ole, ei virhettä koska on määritelty optional, jolloin se on None :)
#     antidote: Optional[str] = None  # Oletusarvo on None

# class DoseRule(BaseModel):
#     notes: Optional[str] = None     # Oletusarvo on None



# def _load_data(self, path: str) -> dict[str, Medicine]: #! tämä on sama kuin Medicine(**med_data), mutta manuaalisesti purettuna. käytä pylance :)
#     with open(path, "r", encoding="utf-8") as f:
#         raw_data = json.load(f)

#     medicines_dict = {}

#     # Käydään JSON-tiedosto läpi lääke kerrallaan
#     for med_name, med_data in raw_data.items():
        
#         # 1. Käsitellään aikuisen säännöt manuaalisesti
#         adult_rules_list = []
#         if "adult" in med_data and "rules" in med_data["adult"]:
#             for rule_dict in med_data["adult"]["rules"]:
#                 # Luodaan jokaisesta säännöstä DoseRule-olio
#                 dose_rule = DoseRule(
#                     condition=rule_dict.get("condition", []),
#                     route=rule_dict.get("route", []),
#                     dose=rule_dict.get("dose", ""),
#                     interval=rule_dict.get("interval", ""),
#                     is_elderly=rule_dict.get("is_elderly"),
#                     requires_iv=rule_dict.get("requires_iv", False),
#                     notes=rule_dict.get("notes")
#                 )
#                 adult_rules_list.append(dose_rule)

#         adult_group = AgeGroupRules(rules=adult_rules_list)

#         # 2. Käsitellään lapsen säännöt manuaalisesti
#         child_rules_list = []
#         if "child" in med_data and "rules" in med_data["child"]:
#             for rule_dict in med_data["child"]["rules"]:
#                 dose_rule = DoseRule(
#                     condition=rule_dict.get("condition", []),
#                     route=rule_dict.get("route", []),
#                     dose=rule_dict.get("dose", ""),
#                     interval=rule_dict.get("interval", ""),
#                     max_single_dose=rule_dict.get("max_single_dose"),
#                     requires_iv=rule_dict.get("requires_iv", False),
#                     notes=rule_dict.get("notes")
#                 )
#                 child_rules_list.append(dose_rule)

#         child_group = AgeGroupRules(rules=child_rules_list)

#         # 3. Kasaillaan lopullinen Medicine-olio
#         medicine_object = Medicine(
#             medicine=med_name,
#             antidote=med_data.get("antidote"),
#             route=med_data.get("route", []),
#             adult=adult_group,
#             child=child_group
#         )

#         # 4. Tallennettaan lääke tulossanakirjaan
#         medicines_dict[med_name] = medicine_object

#     return medicines_dict