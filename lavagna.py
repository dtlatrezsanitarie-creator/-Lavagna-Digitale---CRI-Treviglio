import streamlit as st
import pandas as pd
import os
import requests

# --- CONFIGURAZIONE ---
cartella_script = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(cartella_script, 'Lista articoli.XLSX')
# URL DI CASTEL ROZZONE
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScm1lJ8IhUnT9HwVehKgTbKj9WQomCMagGLTwjOHPi31vPiBQ/formResponse"

st.set_page_config(page_title="CRI Castel Rozzone - Scarico", layout="wide")
st.title("🚑 Lavagna Digitale - CRI Castel Rozzone")

@st.cache_data
def carica_dati():
    if os.path.exists(DB_PATH):
        try:
            # skiprows=1 è fondamentale per la tua nuova lista Excel
            df = pd.read_excel(DB_PATH, skiprows=1)
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except: return None
    return None

df_prodotti = carica_dati()

if df_prodotti is not None:
    cerca = st.text_input("COSA HAI PRESO?", "").strip().lower()
    if cerca:
        risultati = df_prodotti[df_prodotti['Descrizione'].astype(str).str.contains(cerca, case=False, na=False)]
        if not risultati.empty:
            for _, row in risultati.head(10).iterrows():
                nome_articolo = str(row['Descrizione'])
                codice_mambu = str(row['Barcode'])
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"### {nome_articolo}")
                        st.caption(f"Codice: {codice_mambu}")
                    with col2:
                        qta = st.number_input("Pezzi", min_value=1, value=1, key=f"q_{codice_mambu}")
                    with col3:
                        st.write(" ")
                        if st.button("SCARICA ✅", key=f"btn_{codice_mambu}", use_container_width=True):
                            payload = {
                                "entry.1921919747": nome_articolo,
                                "entry.1949015185": codice_mambu,
                                "entry.1928057596": str(qta)
                            }
                            try:
                                r = requests.post(FORM_URL, data=payload)
                                if r.status_code == 200:
                                    st.balloons()
                                    st.success(f"REGISTRATO: {qta} {nome_articolo}")
                                else:
                                    st.error("Errore Google Form.")
                            except:
                                st.error("Errore connessione.")
