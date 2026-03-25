import streamlit as st
import random
import csv
from collections import defaultdict
import os

# cartella domande
BASE_PATH = "./domande"

FILES = {
    "Utilizzatori": "utilizzatori.csv",
    "Distributori": "distributori.csv",
    "Consulenti": "consulenti.csv",
}

PASS_SCORE = 32


# -------------------------
# SIDEBAR
# -------------------------

st.set_page_config(page_title="Simulatore Patentino", layout="wide")

st.sidebar.title("📂 Selezione categoria")

categoria = st.sidebar.radio(
    "Esame per:",
    list(FILES.keys())
)

CSV_PATH = os.path.join(BASE_PATH, FILES[categoria])

# spazio flessibile per spingere in basso
st.sidebar.markdown("<br><br><br><br><br><br><br><br>", unsafe_allow_html=True)

st.sidebar.markdown("---")

st.sidebar.markdown("Questo progetto è gratuito ed è sviluppato nel tempo libero. Se ti ha aiutato a studiare, puoi supportarlo con un piccolo contributo. Grazie!")

st.sidebar.markdown(
    """
    <a href="https://www.buymeacoffee.com/momodepa" target="_blank">
        <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" 
             alt="Buy Me A Coffee" 
    </a>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

st.sidebar.markdown("📩 Hai trovato un errore o hai dei suggerimenti per migliorarlo? [Contattami](mailto:emanueledepaoli1@gmail.com)")

# -------------------------
# CARICAMENTO DOMANDE
# -------------------------

@st.cache_data
def leggi_domande(csv_path):

    domande = defaultdict(list)

    with open(csv_path, newline="", encoding="utf-8") as csvfile:

        reader = csv.DictReader(csvfile, delimiter=";")

        for row in reader:

            pti = int(row["pti"])

            domanda = {
                "domanda": row["domanda"].strip(),
                "pti": pti,
                "corretta": row["risp_corretta"].strip().upper(),
                "opzioni": {
                    "A": row["risp_A"].strip(),
                    "B": row["risp_B"].strip(),
                    "C": row["risp_C"].strip(),
                },
            }

            domande[pti].append(domanda)

    return domande


# -------------------------
# GENERAZIONE ESAME
# -------------------------

def genera_esame(domande):

    n1 = random.randint(0, 10)
    n3 = n1
    n2 = 20 - 2 * n1

    estratte = (
        random.sample(domande[1], n1)
        + random.sample(domande[2], n2)
        + random.sample(domande[3], n3)
    )

    random.shuffle(estratte)

    return estratte


# -------------------------
# CORREZIONE
# -------------------------

def correggi_esame(esame, risposte):

    punteggio = 0
    errori = []

    for i, domanda in enumerate(esame):

        risposta = risposte.get(i)

        if risposta == domanda["corretta"]:
            punteggio += domanda["pti"]

        else:

            errori.append({
                "domanda": domanda["domanda"],
                "tua_lettera": risposta,
                "tua_risposta": domanda["opzioni"].get(risposta, "nessuna risposta"),
                "corretta_lettera": domanda["corretta"],
                "corretta_risposta": domanda["opzioni"][domanda["corretta"]],
                "pti": domanda["pti"]
            })

    return punteggio, errori


# -------------------------
# UI
# -------------------------

st.title("🌱 Simulatore Esame Patentino Fitosanitario")
st.subheader(f"Quesiti per {categoria}")

domande = leggi_domande(CSV_PATH)

# -------------------------
# STATE
# -------------------------

if "esame" not in st.session_state:
    st.session_state.esame = None
    st.session_state.risposte = {}

# reset automatico quando cambio categoria
if "categoria_corrente" not in st.session_state:
    st.session_state.categoria_corrente = categoria

if st.session_state.categoria_corrente != categoria:
    st.session_state.esame = None
    st.session_state.risposte = {}
    st.session_state.categoria_corrente = categoria

# -------------------------
# GENERA ESAME
# -------------------------

if st.button("🎯 Genera nuovo esame"):

    st.session_state.esame = genera_esame(domande)
    st.session_state.risposte = {}

# -------------------------
# MOSTRA ESAME
# -------------------------

if st.session_state.esame:

    esame = st.session_state.esame

    for i, q in enumerate(esame):

        st.markdown(f"### Domanda {i+1}")
        st.write(q["domanda"])

        scelta = st.radio(
            "Risposta",
            ["A", "B", "C"],
            format_func=lambda x: q["opzioni"][x],
            key=f"q{i}",
        )

        st.session_state.risposte[i] = scelta

        st.divider()

    # -------------------------
    # CONSEGNA
    # -------------------------

    if st.button("✍️ Correzione esame"):

        punteggio, errori = correggi_esame(
            esame,
            st.session_state.risposte
        )

        st.header("Risultato")

        st.metric("Punteggio", f"{punteggio}/40")

        if punteggio >= PASS_SCORE:
            st.success("✅ ESAME SUPERATO")
        else:
            st.error("❌ ESAME NON SUPERATO")

        st.progress(punteggio / 40)

        if errori:

            st.subheader("Risposte sbagliate")

            for e in errori:

                st.write("**Domanda:**", e["domanda"])
                st.write(f"Tua risposta: {e['tua_risposta']}")
                st.write(f"Corretta: {e['corretta_risposta']}")
                st.write(f"Punti domanda: {e['pti']}")

                st.divider()

        else:
            st.success("🎉 Tutte corrette!")