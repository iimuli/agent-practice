import requests
from bs4 import BeautifulSoup
import streamlit as st

@st.cache_data(ttl=3600)
def fetch_live_menus() -> dict:
    url = "https://www.lounasmenu.fi/lahti/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        menus = {}

        # Etsitään ravintolakortit sivuston rakenteesta
        # (Voit tarkentaa tätä sen mukaan, mikä div-luokka pitää korttia sisällään)
        cards = soup.select("div.mn-item") # Tarkista vielä vastaako luokka täysin
        
        for card in cards:
            # Etsitään ravintolan nimi otsikosta tai title-attribuutista
            title_el = card.find("h2") or card.find(attrs={"title": True})
            name = title_el.get_text(strip=True) if title_el else "Tuntematon ravintola"
            
            # Etsitään lounaslistan rivit kortin sisältä
            rows = card.select(".min-row, p.min-txt")
            menu_lines = [row.get_text(strip=True) for row in rows if row.get_text(strip=True)]
            
            if menu_lines:
                menus[name] = "\n".join(menu_lines)

        return menus
    except Exception as e:
        print(f"Virhe lounaslistojen haussa: {e}")
        return {}