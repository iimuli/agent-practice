import os
import json
from dotenv import load_dotenv
from groq import Groq
import tools

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

AVAILABLE_FUNCTIONS = {
    # "get_weather_forecast": tools.get_weather_forecast,
    # "search_local_venues": tools.search_local_venues,
    "check_medicine_dose": tools.check_medicine_dose,
}

def run_interactive_agent():
    #! hässäkä toimii syöte listana (messages). esimmäinen viesti kertoo AI:lle roolin ja siihen liittyvät nuanssit
    messages = [
    {
        "role": "system", 
        "content": (
            "Olet avustava lääke- ja hoito-ohjeen tuottaja ensihoidolle. "
            "TÄRKEÄÄ: Tämä on demo/portfolio, eikä tätä käytetä oikeasti terveydenhuollossa! "
            "Käyttäjä kertoo oireen tai lääkkeen, ja antaa tarvittavat parametrit kuten ikä, paino, oire, tarve, ja sinun tehtävänäsi on käyttää annettuja työkaluja ja ohjeita"
            "määrittääksesi tilanteeseen sopivat hoito- ja lääke-ohjeet."
        )
    }
]
    print("Tapahtuma-agentti valmiina! (Kirjoita 'poistu' lopettaaksesi)")

    while True:
        user_input = input("\nSinä: ")

        if user_input.lower() in ['poistu', 'exit', 'quit']:
            print("Lopetetaan! :)")
            break

        #lisätään käyttänä inputti listaan
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create( #!vastaus, kutsutaan API
            model="qwen/qwen3.8-27b", #AI malli
            messages=messages, #mitä syötteitä käyttää, tässä tilanteessa aiemmin laitettut messages
            tools = tools.tools_spec, #työkalut
            tool_choice="auto" #vastauksen tyyppi, käyttääkö annettuja työkaluja
        )

        response_message = response.choices[0].message #valitaan tässä ensimmäinen vaihtoehto listalta eli index 0
        messages.append(response_message) #lisätään AI:n vastaus listaan


        #! työkalujen käsittelyt
        if response_message.tool_calls: #jos AI päättää käyttää työkaluja...
            for tool_call in response_message.tool_calls: #jokaista työkalua kohti...
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f" [Agentti hakee tietoa: {func_name}]")

                func_to_call = AVAILABLE_FUNCTIONS[func_name] #haetaan funktio ennalta määritetystä kirjastosta
                func_response = func_to_call(**args) #työkalu ja halutut argumentit

                messages.append({ #lisätään vastaus message listaan
                    "tool_call_id": tool_call.id, #työkalun id
                    "role": "tool", #rooli, eli tool. AI tiedostaa kuka loi vastauksen (system, user, tool)
                    "name": func_name, #työkalun nimi
                    "content": func_response, #työkalusta palautuva data, esim tässä tilanteessa ruokapaikat ja niihin liittyvä data
                })

                #! pyydetään lopullinen vastaus työkalujen perusteella
                final_response = client.chat.completions.create(
                    model="qwen/qwen3.8-27b",
                    messages=messages #heitetään lopullinen viesti lista ai:lle tulkittavaksi
                )
                final_message = final_response.choices[0].message #valitaan ensimmäinen listalta
                messages.append(final_message) #lisätään listaan lopullinen vastaus
                print(f"\nAgentti:\n{final_message.content}")
        else:
            #jos ei työkaluja käytössä, tulostetaan suora vastaus
            print(f"\nAgentti:\n{response_message.content}")

    


def run_event_agent(prompt: str):
    messages = [
        {"role": "system", "content": "Olet avustava tapahtumasuunnittelija. Käytä saatavilla olevia työkaluja ja luo valmis raportti."},
        {"role": "user", "content": prompt}
    ]

    print("Agentti aloittaa suorituksen... \n")


    while True:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=messages,
            tools = tools.tools_spec,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        messages.append(response_message)

        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                print(f"Agentti kutsuu työkalua {function_name}")

                function_to_call = AVAILABLE_FUNCTIONS[function_name]
                function_response = function_to_call(**function_args)

                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                })

        else:
            print("\n Agentti sai tehtävän valmiiksi!")
            final_content = response_message.content
            break

    with open ("event_brief.md", "w", encoding="utf-8") as f:
        f.write(final_content)


    print("Raportti tallennettu tiedostoon: event_brief.md")


def run_medicine_instruction_test(age: str, condition: str, medicine: str, route: list[str], weight: str, indication: str):
    print(tools.check_medicine_dose(age, condition, medicine, route, weight, indication))

if __name__ == "__main__":

    run_medicine_instruction_test("70", "", "midatsolaami", ["i.n."], "", "")



 #lääke annettu defaulttina, ei tarvii selata hoito ohjeita läpi
 #def check_medicine_dose(age: str = "", condition: str = "", medicine: str = "", route: str = "", weight: str = "", indication: str = "")  -> str:







