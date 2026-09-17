from src.tools.dose_checker import check_medicine_dose_tool
from src.tools.symptoms_checker import check_symptoms_tool


# Kytketään agentin kutsuma funktion nimi toteutukseen
AVAILABLE_FUNCTIONS = {
    "check_medicine_dose_tool": check_medicine_dose_tool,
    "check_symptoms_tool": check_symptoms_tool
}

tools_spec = [
{
        "type": "function",
        "function": {
            "name": "check_medicine_dose_tool",
            "description": "Laskee valitun lääkkeen annoksen ja antoreitin.",
            "parameters": {
                "type": "object",
                "properties": {
                    "condition": {
                        "type": "string",
                        "description": "Oire tai tila, esim. 'kouristus'"
                    },
                    "age_group": {
                        "type": "string",
                        "enum": ["adult", "child"]
                    },
                    "has_iv_access": {
                        "type": "boolean"
                    },
                    "preferred_medicine": {
                        "type": "string",
                        "description": "Valitun lääkkeen nimi, esim. 'midatsolaami'"
                    },
                    "weight_kg": {
                        "type": ["number", "null"]
                    },
                    "is_elderly": {
                        "type": "boolean"
                    }
                },
                "required": ["condition", "age_group"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_symptoms_tool",
            "description": "Etsii sopivat lääkkeet tietokannasta oirekuvan tai oirekuvien perusteella.",
            "parameters": {
                "type": "object",
                "properties":{
                    "symptoms":{
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lista oireista, esim. ['levoton'] tai ['kouristaa']"
                    },
                    "age_group": {
                        "type": "string",
                        "description": "Ikäryhmä, esim. 'adult' tai 'child'"
                    },
                    "has_iv_access": {
                        "type": "boolean",
                        "description": "Onko potilaalla toimiva i.v.-yhteys"
                    },
                    "weight_kg": {
                        "type": "number",
                        "description": "Lapsipotilaan paino kiloina"
                    },
                    "is_elderly": {
                        "type": "boolean",
                        "description": "Onko potilas iäkäs (>70v)"
                    }
                },
                "required": ["symptoms", "age_group"]
                }
            }
    }
    
]
