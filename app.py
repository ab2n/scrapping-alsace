import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.title("Scraping des élus des cantons alsaciens")

# URL cible (à modifier selon la page que tu veux scraper)
url = st.text_input("Entrez l'URL de la page à scraper :", "https://exemple.com/cantons")

if st.button("Lancer le scraping"):
    try:
        # Récupération du contenu HTML
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extraction du texte brut
        text = soup.get_text(separator="\n")

        # Découper par canton
        lines = [l.strip() for l in text.split("\n") if l.strip() != ""]

        data = []
        current_canton = None
        current_names = []

        # Mots à ignorer
        blacklist = [
            "Une question ?", "Conseiller d'Alsace", "Conseillère d'Alsace",
            "Twitter", "Facebook", "En savoir plus sur ce canton"
        ]

        for line in lines:
            if line.startswith("Canton de"):
                # Sauvegarde du canton précédent
                if current_canton and current_names:
                    row = {"Canton": current_canton}
                    for i, name in enumerate(current_names, start=1):
                        row[f"Élu {i}"] = name
                    data.append(row)
                current_canton = line
                current_names = []
            elif line not in blacklist and current_canton:
                # Cas où c'est un élu (on suppose que ce n’est pas dans blacklist)
                # Petit filtre : on ignore les phrases trop longues (>6 mots)
                if len(line.split()) <= 5:
                    current_names.append(line)

        # Sauvegarde du dernier canton
        if current_canton and current_names:
            row = {"Canton": current_canton}
            for i, name in enumerate(current_names, start=1):
                row[f"Élu {i}"] = name
            data.append(row)

        # Affichage dans un tableau
        df = pd.DataFrame(data)
        st.dataframe(df)

    except Exception as e:
        st.error(f"Erreur lors du scraping : {e}")

