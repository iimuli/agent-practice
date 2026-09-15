# 🚑 Ensihoidon Lääkehoidon Avustaja (Demo & Oppimisprojekti)

Moi! Olen alasta innostunut aloitteleva kehittäjä, ja tämä on oppimisprojektini, jossa tutkin tekoälyn hyödyntämistä sekä **Function Calling (Tools)** -toiminnallisuutta sääntöpohjaisessa tiedonhaussa.

Projektin tavoitteena oli oppia rakentamaan sovellus, joka yhdistää kielimallin (LLM) kyvyn ymmärtää vapaamuotoista tekstiä ja taustalla toimivan Python-laskentalogiikan.

---

> ⚠️ **TÄRKEÄ DISCLAIMEER / VASTUUVAPAUSLAUSEKE:**  
> Tämä projekti on tehty **ainoastaan oppimis- ja portfoliotarkoitukseen**. Sovellusta **EI SAA** käyttää todellisessa hoitotyössä tai kliinisessä päätöksenteossa!

---

## 🛠️ Mitä opiskelin tätä tehdessä?

* **Streamlit:** Nopean käyttöliittymän rakentaminen chat-käyttöliittymällä (`st.chat_message`, `st.session_state`).
* **LLM Tool Calling / Function Calling:** Miten saadaan kielimalli kutsumaan omia Python-funktioita (`check_medicine_dose`) suoran tekstintuottamisen sijaan.
* **Tietoturva & Ympäristömuuttujat:** API-avainten suojautuminen `.env`-tiedostolla ja `.gitignore`-hallinta.

## 🚀 Teknologiat

* **Kieli:** Python 3.10+
* **Käyttöliittymä:** [Streamlit](https://streamlit.io/)
* **Kielimallirunsaat:** Groq API / OpenAI
* **Muut:** `python-dotenv`

---

## 💻 Miten ajat projektin paikallisesti?

1. **Kloonaa tämä repositorio:**
   ```bash
   git clone [https://github.com/kayttajatunnus/projekti-nimi.git](https://github.com/kayttajatunnus/projekti-nimi.git)
   cd projekti-nimi