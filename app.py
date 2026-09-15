"""
Ensihoidon lääkehoidon avustaja - Käyttöliittymä ja agenttilogiikka - Harjoitusprojekti

Tämä Streamlit-sovellus toimii käyttöliittymänä tekoälyavustajalle, joka auttaa
ensihoidon lääke- ja annosteluohjeiden hakemisessa koodattujen sääntöjen pohjalta.

VAROITUS / DISCLAIMER:
Tämä projekti on kehitetty ainoastaan portfolio- ja demonstraatiotarkoitukseen.
Sovellusta EI SAA käyttää todellisessa lääketieteellisessä päätöksenteossa tai
potilastyössä.

Tekijä: Eemeli Väisänen
Teknologiat: Python, Streamlit, LLM (Function Calling / Tools)
"""

import streamlit as st
import json
import os
from dotenv import load_dotenv
from groq import Groq
import tools

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY")) #api avain joka löytyy .env tiedostosta, piilotettu .gitignorella githubista

st.title("Hoito-ja lääkeohje avustaja")
st.write("Kyseessä DEMO, tällä hetkellä teemana ainoastaan kouristelevan potilaan hoito ensihoidossa. Tämä demo käyttää Päijät-Hämeen omia hoito- ja lääkeohjeita.\nHUOM! Tätä demoa EI tule käyttää oikeassa hoitotyössä.")

# alustetaan chatin historia aloittaessa
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",  #annetaan agentilel toimintaohjeet, tässä rajattu vastuasmallit ja aihealueet 
            "content": (
                "Olet lääkehoidon avustaja ensihoidolle. TÄRKEÄÄ: Tämä on demo/portfolio, eikä tätä käytetä oikeasti terveydenhuollossa!\n\n"
                "TEHTÄVÄ:\n"
                "Määritä potilaan oireiden ja tietojen perusteella sopiva lääke, annos ja antoreitti käyttämällä saatavilla olevia työkaluja.\n\n"
                "AIHEALUEEN RAJAUS (KRIITTINEN):\n"
                "- Vastaa AINOASTAAN ensihoidon lääkeohjeisiin ja kouristelevan potilaan hoitoon liittyviin kysymyksiin.\n"
                "- Jos käyttäjä kysyy aiheen ulkopuolisia asioita (esim. ruoka, sää, yleistieto), KIELTÄYDY vastaamasta ja sano lyhyesti: 'Olen erikoistunut vain ensihoidon lääkeohjeisiin. Voinko auttaa kouristelevan potilaan hoidossa?'\n\n"
                "SÄÄNNÖT:\n"
                "1. Kutsut välittömästi `check_medicine_dose`-työkalua saaduilla parametreilla.\n"
                "2. Jos työkalu palauttaa virheen puuttuvista tiedoista (esim. lapsen paino), pyydä se lyhyesti.\n"
                "3. Kun työkalu palauttaa valmiin ohjeen, toista se sellaisenaan ilman omia lisäyksiä."
            )
        }
    ]

# näytetään aiempi keskusteluhistoria (piilotetaan system- ja tool-viestit)
for msg in st.session_state.messages:
    role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", None)
    content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", None)

    if role not in ["system", "tool"] and content:
        with st.chat_message(role):
            st.markdown(content)

# käyttäjän syötteet
if user_input := st.chat_input("Kirjoita viesti..."):
    
    #  kirjataan käyttäjän viesti chattiin ja session viesteihin appendilla
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # agentin suoritusympäristö
    with st.chat_message("assistant"):
        # ajetaan while silmukassa niin kauan, kunnes malli päättää tuottaa lopullisen tekstivastauksen
        while True:
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b", 
                messages=st.session_state.messages,
                tools=tools.tools_spec,
                tool_choice="auto", #"required" jos halutaan pakottaa pelkkien työkalun käyttöä
                max_tokens=800
            )

            response_message = response.choices[0].message

            # haluaako malli käyttää työkaluja?
            if response_message.tool_calls:
                
                st.session_state.messages.append(response_message) # tllennetaan mallin tekemä työkalupyyntö historiaan muistiin

                
                for tool_call in response_message.tool_calls: # suoritetaan yksitellen kaikki mallin pyytämät työkalukutsut
                    func_name = tool_call.function.name
                    raw_args = tool_call.function.arguments or "{}"
                    args = json.loads(raw_args)

                   
                    with st.status(f"Agentti hakee tietoa työkalulla: `{func_name}`...", expanded=True) as status:  # käyttäjälle visuaalinen status agentin tekemisestä
                        func_to_call = tools.AVAILABLE_FUNCTIONS[func_name]
                        func_response = func_to_call(**args)
                        status.update(label=f"Työkalu `{func_name}` suoritettu!", state="complete", expanded=False)


                    st.session_state.messages.append({ # palautetaan alustava tulos mallille historiaan
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": func_response,
                    })
            else:
                # kun työkaluja ei pyydetä/käytetä enään, näytetään valmis vastaus
                final_text = response_message.content
                st.markdown(final_text)
                           
                st.session_state.messages.append({"role": "assistant", "content": final_text})  # tekstin tallentaminen historiaan
                break