import streamlit as st
import random
import csv
from collections import defaultdict

CSV_PATH = "domande.csv"

# domande da 1,2,3 punti
# 20 domande estratte in modo tale che il totale dei punti sia 40
PASS_SCORE = 32

# -------------------------
# CARICAMENTO DOMANDE
# -------------------------

@st.cache_data
def leggi_domande():

    domande = defaultdict(list)

    with open(CSV_PATH, newline="", encoding="utf-8") as csvfile:

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
    n2 = 20 - 2 * n3

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

st.set_page_config(page_title="Simulatore Patentino", layout="wide")

st.title("🌱 Simulatore Esame Regione Piemonte per Patentino Fitosanitario")
st.subheader("Quesiti per utilizzatori")

domande = leggi_domande()


# -------------------------
# GENERA ESAME
# -------------------------

# inizializzazione state
if "esame" not in st.session_state:
    st.session_state.esame = None
    st.session_state.risposte = {}

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

                st.write(
                    f"Tua risposta: {e['tua_risposta']}"
                )

                st.write(
                    f"Corretta: {e['corretta_risposta']}"
                )

                st.write(f"Punti domanda: {e['pti']}")

                st.divider()

        else:
            st.success("🎉 Tutte corrette!")