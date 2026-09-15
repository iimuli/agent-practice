"""
Ensihoidon lääkehoidon avustaja - Työkalut ja laskentalogiikka - Harjoitusprojekti

Tämä tiedosto sisältää LLM-agentin käyttämät työkalufunktiot (Function Calling)
sekä lääkeohjeiden filtteröinti- ja muotoilulogiikan JSON-tietokannasta.

VAROITUS / DISCLAIMER:
Laskentalogiikka ja lääketiedot ovat demoversioita. Ei sovellu kliiniseen käyttöön.

Tekijä: Eemeli Väisänen
"""

import json
import re


with open("instructions/instruction_medicine.json", "r", encoding="utf-8") as file: #luetaan lääketiedosto, nyt vain midatsolaami
    INSTRUCTIONS_MEDICINE = json.load(file)

with open("instructions/instruction_seizure.json", "r", encoding="utf-8") as file: #luetaan tulevaisuudessa hoito-ohjeet
    INSTRUCTIONS_TREATMENT = json.load(file)


def determine_patient_condition(parameters: list[str]) -> str: #alustava funktio, kun käyttäjä kertoo potilaan oireista
    return ""

def determine_medicine_for_condition(condition: str) -> str: #selvitetään oireiden perusteella käytettävä lääkitys
    return ""

#tässä demo mallissa vielä toistaiseksi lyöty ylemmän funktiot tähän samaan, sillä oletuksena kouristava/midatsolaami (toistaiseksi)
def check_medicine_dose(age: str = "", condition: str = "", medicine: str = "", route: str = "", weight: str = "", indication: str = "")  -> str:

    if age == "": #jos ikäluokkaa ei tiedossa, lääkeohjetta ei pystytä luomaan
        return json.dumps({"error": "Ole hyvä ja kerro potilaan ikäryhmä (lapsi, aikuinen, vanhus) tai tarkka ikä"}, ensure_ascii=False)

    if condition == "" and medicine == "": #jos oiretta tai haluttua lääkettä ei tiedossa, lääkeohjetta ei pystyty äluomaan
        return json.dumps({"error": "Ole hyvä ja kerro potilaan oirekuva tai tarvittava lääke."}, ensure_ascii=False)

    
    search_term = (condition or "") + " " + (indication or "") # yhistetään hakusanat, jotta kouristus löytyy kummasta tahansa parametrista...
    search_term = search_term.lower()
    
    if not medicine and condition: #varmistetaan että annetuissa parametreissa on tarvittavat tiedot
        if "kourist" in condition.lower() or "sekav" in condition.lower() or "ketami" in condition.lower():
            medicine = "midatsolaami"
        else:
            return json.dumps({"error": f'Ei löydy sopivaa lääkettä oireelle "{condition}". Mainitse lääkkeen nimi erikseen.'}, ensure_ascii=False)



    med_data = INSTRUCTIONS_MEDICINE.get(medicine) 
    if not med_data: #lääkeohje puuttuu syystä tai toisesta
        return f"Lääkeohjetta kyseisellä lääkkellä ({medicine}) ei löydettävissä tietokannasta."

    age_lower = age.lower().strip()
    age_group = ""
    is_elderly = False
    current_weight = None

    is_child = "lapsi" in age_lower or "child" in age_lower #tarkastetaan onko lapsi potilas
    if not is_child and age.isdigit():
        if int(age) < 18:
            is_child = True

    if is_child:
        age_group = "child"
        if not weight: #paino pakollinen lapsipotilaille tässä lääkkeessä. Myöhemmin voidaan tarkastaa suoraan lääkkeestä onko sille määritelty paino vaatimusta
            return json.dumps({"error": "Ole hyvä ja anna lapsen paino (kg), jotta annos voidaan laskea."}, ensure_ascii=False)
        try:
            current_weight = float(weight)
        except ValueError:
            return json.dumps({"error": "Painon pitää olla numero (esim. '13' tai '12.5')."})
    else: 
        age_group = "adult"
        if "vanhus" in age_lower or "elderly" in age_lower:  #onko vanhus?
            is_elderly = True
        elif age.isdigit() and age >= 70: 
            is_elderly = True

    safe_route = str(route).lower() if route else "" #jos route määritely, muuta se STR. muutoin se on tyhjä "" reitit ei aina tiedossa 
    has_iv = False #oletus on ei iv yhteyttä, ellei käyttäjä ole sitä määritellyt

    if "ei" in safe_route or "ilman" in safe_route or "no " in safe_route: #kattoo onko i.v. antoreiteissä.
        has_iv = False
    elif "i.v." in safe_route or "suoniyhteys" in safe_route or "iv" in safe_route or "i.v" in safe_route:
        has_iv = True

    rules = med_data[age_group]["rules"] #hakee säännöt kohdatasta "adult" tai "children". tässä kohtaa midatsolaami ohjeet koodattuna vain.
    matching_instructions = []  #tähä kaikki sopivat ohjeet pakettiin

    route_priority = med_data.get("route", []) #ottaa arraysta järjestyksessä antoreitin, eli jos ei iv. yhteyttä, ehdottaa in. ensisijaisesti

    def sort_by_route_priority(instruction):  # apufunktio, joka järjestää lääkeohjeen antoreitti listan mukaiseen järjestykseen (iv ensisijainen jne)
        r = instruction.get("route", "")
        if r in route_priority:
            return route_priority.index(r)
        return 99


    for instructions in rules:
        rule_condition = instructions.get("condition", "").lower()
        
        # eka katotaan täsmääkö oire
        if search_term.strip():
            if "kourist" in search_term and "kourist" not in rule_condition:
                continue
            if "ketam" in search_term and "ketam" not in rule_condition:
                continue
            if "levot" in search_term and "delirium" not in rule_condition and "levot" not in rule_condition:
                continue

        # onko iv yhteyttä
        if safe_route:
            if instructions.get("requires_iv") != has_iv:
                continue
                
        #  onko aikuinen/vanhus
        if age_group == "adult" and "is_elderly" in instructions:
            if instructions.get("is_elderly") != is_elderly:
                continue

        # jos päästään tänne asti, sääntö on validi
        if age_group == "child" and "/kg" in instructions.get("dose", ""):
            dose_str = instructions.get("dose")
            match = re.search(r"[\d\.]+", dose_str)
            if match and current_weight:
                dose_value = float(match.group())
                calculated_dose = dose_value * current_weight

                has_max_value = instructions.get("max_single_dose")
                if has_max_value:
                    max_match = re.search(r"[\d\.]+", has_max_value)
                    if max_match:
                        max_limit = float(max_match.group())
                        calculated_dose = min(calculated_dose, max_limit)

                res_copy = instructions.copy()
                res_copy["calculated_dose"] = f"{calculated_dose}mg"
                matching_instructions.append(res_copy)
        else:
            matching_instructions.append(instructions)

            

    if matching_instructions:
        matching_instructions.sort(key=sort_by_route_priority)
       
        best_match = matching_instructions[0]  #tetaan parhaiten sopiva ohje (ensimmäinen listassa)
        formatted_result = format_instruction_response(best_match, medicine)   # Muotoillaan se valmiiksi tekstiksi apufunktiolla      
 
        return formatted_result
        
    return json.dumps({"error": f"Sopivaa lääkeohjetta ei löytynyt ({age_group}) annetuilla tiedoilla."}, ensure_ascii=False)

def format_instruction_response(instruction: dict, medicine_name: str) -> str:
    # vastausrakenne oletus joka löytyy aina, jotta agentin käyttö on suorasukaista
    lines = [
            f"**Lääke:** {medicine_name.capitalize()}",
            f"**Antoreitti:** {instruction.get('route', '')}",
            f"**Annos:** {instruction.get('calculated_dose', instruction.get('dose', ''))}",
        ]
    # lopuksi lisätään valinnaiset kentät JOS!!! ne löytyvät datasta
    if instruction.get("interval"):
        lines.append(f"**Toistettavuus:** {instruction.get('interval')}")
        
    if instruction.get("notes"):
        lines.append(f"**Huomioitavaa:** {instruction.get('notes')}")
        
    return "\n".join(lines)

tools_spec = [ #agentille annetut ohjeet funktion käyttöön liittyen
    {
        "type": "function",
        "function": {
            "name": "check_medicine_dose",
            "description": "Hakee lääkkeen annoksen ja antoreitin. Palauttaa JSON-listan sopivista vaihtoehdoista..",
            "parameters":{
                "type": "object",
                "properties": {
                    "age": {"type": ["string", "null"],
                            "description": "Potilaan ikäryhmä: 'lapsi', 'aikuinen', 'vanhus', tai ikä vuosina (aikuinen yli 17, vanhus yli 69)."},
                    "condition": {"type": ["string", "null"],
                                  "description": "Potilaan oire, esim. 'kouristus'."},
                    "medicine": {"type": ["string", "null"],
                                 "description": "Tiedetty lääke. Voi jättää tyhjäksi, jos työkalu osaa päätellä sen oireesta."},
                    "route": {"type": ["string", "null"],
                              "description": "Tieto suoniyhteydestä, esim 'i.v.' tai 'ei iv' tai 'ilman i.v.'"},
                    "weight": {"type": ["string", "null"],
                               "description": "Pakollinen VAIN lapsille annoksen laskemiseen (kg)."},
                    "indication": {"type": ["string", "null"],
                                   "description": "Lisätieto oireesta."}
                }
            }
        }
    }
]

AVAILABLE_FUNCTIONS = { #käytössä olevat funktiot toistaiseksi
    "check_medicine_dose": check_medicine_dose
}

