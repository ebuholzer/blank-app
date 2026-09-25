# ============================================================
# TRAVELMATCH
# Einfacher und nutzerfreundlicher Reiseziel-Recommender
# ============================================================


# ------------------------------------------------------------
# 1. BIBLIOTHEKEN
# ------------------------------------------------------------

# Streamlit erstellt die Web-App.
import streamlit as st

# math brauchen wir für die Berechnung des Match-Scores.
import math


# ============================================================
# 2. SEITENEINSTELLUNGEN
# ============================================================

# Grundeinstellungen der Webseite.
st.set_page_config(
    page_title="TravelMatch",
    page_icon="🌍",
    layout="wide"
)


# ============================================================
# 3. KLEINE DESIGN-VERBESSERUNGEN
# ============================================================

# Etwas CSS macht die App ruhiger und kompakter.
st.markdown(
    """
    <style>

    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    div.stButton > button {
        width: 100%;
        min-height: 3.2rem;
        border-radius: 12px;
        font-size: 1rem;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 4. TITEL
# ============================================================

# Haupttitel.
st.title("🌍 TravelMatch")

# Kurze Erklärung.
st.write(
    """
    Finde Reiseziele, die zu deiner Reisezeit,
    deinem Budget und deinen Interessen passen.
    """
)

st.divider()


# ============================================================
# 5. DATENSTRUKTUR
# ============================================================
#
# Für jedes Land speichern wir:
#
# - Name
# - Region
# - Tagesbudget für drei Reisestile
# - durchschnittliche Temperatur pro Monat
# - Bewertungen für verschiedene Reiseinteressen
#
#
# BUDGET
# ------------------------------------------------------------
#
# Für jedes Land gibt es drei Tagesbudgets:
#
# Sparsam
# Komfort
# Luxuriös
#
# Die Werte sind ungefähre CHF-Beträge pro Person und Tag.
#
# Sie basieren auf den zuvor recherchierten
# Budget- / Mid-Range- / Luxury-Werten von Budget Your Trip.
#
# USD-Werte wurden mit dem zuvor recherchierten
# SNB-Wechselkurs in CHF umgerechnet und gerundet.
#
# Die Werte sind Richtwerte und keine garantierten Preise.
#
#
# AKTIVITÄTEN
# ------------------------------------------------------------
#
# Strand, Kultur, Essen, Natur und Nightlife:
#
# 1 = geringe Eignung
# 5 = sehr hohe Eignung
#
# Diese Werte sind weiterhin vereinfachte
# Demo-Bewertungen für den Prototyp.
#
#
# TEMPERATUREN
# ------------------------------------------------------------
#
# Die Monatswerte sind vereinfachte durchschnittliche
# Temperaturwerte für eine typische Destination.
#
# Dadurch funktioniert die App ohne externe Wetter-API
# und ist wesentlich stabiler.
# ============================================================


# Hilfsfunktion:
# Sie macht die Länder-Daten unten deutlich übersichtlicher.
def land(
    name,
    region,
    budgets,
    temperaturen,
    strand,
    kultur,
    essen,
    natur,
    nightlife
):

    # Ein Dictionary mit allen Daten des Landes zurückgeben.
    return {
        "land": name,
        "region": region,

        # Tagesbudgets der drei Reisestile.
        "budgets": {
            "Sparsam": budgets[0],
            "Komfort": budgets[1],
            "Luxuriös": budgets[2]
        },

        # 12 Monatswerte von Januar bis Dezember.
        "temperaturen": temperaturen,

        # Bewertungen der Reiseinteressen.
        "strand": strand,
        "kultur": kultur,
        "essen": essen,
        "natur": natur,
        "nightlife": nightlife
    }


# ============================================================
# 6. 50 REISELÄNDER
# ============================================================

reiseziele = [

    # ========================================================
    # EUROPA
    # ========================================================

    land(
        "Portugal",
        "Europa",
        (65, 159, 373),
        [15, 16, 18, 19, 22, 25, 28, 28, 26, 22, 18, 16],
        5, 4, 5, 4, 4
    ),

    land(
        "Spanien",
        "Europa",
        (70, 178, 452),
        [12, 13, 16, 18, 22, 27, 30, 30, 26, 21, 16, 13],
        5, 5, 5, 4, 5
    ),

    land(
        "Italien",
        "Europa",
        (77, 194, 485),
        [8, 10, 13, 17, 21, 25, 28, 28, 24, 19, 13, 9],
        4, 5, 5, 4, 4
    ),

    land(
        "Griechenland",
        "Europa",
        (83, 208, 514),
        [10, 11, 14, 18, 23, 28, 31, 31, 27, 22, 17, 12],
        5, 5, 4, 4, 4
    ),

    land(
        "Kroatien",
        "Europa",
        (56, 142, 358),
        [7, 9, 13, 17, 22, 26, 29, 29, 24, 19, 13, 9],
        5, 4, 4, 5, 3
    ),

    land(
        "Frankreich",
        "Europa",
        (89, 251, 789),
        [6, 7, 11, 14, 18, 22, 25, 25, 21, 16, 10, 7],
        4, 5, 5, 4, 4
    ),

    land(
        "Niederlande",
        "Europa",
        (82, 204, 507),
        [5, 6, 9, 13, 17, 20, 22, 22, 19, 14, 9, 6],
        2, 5, 4, 3, 4
    ),

    land(
        "Belgien",
        "Europa",
        (66, 163, 387),
        [5, 6, 9, 12, 16, 19, 21, 21, 18, 14, 9, 6],
        2, 5, 5, 3, 4
    ),

    land(
        "Deutschland",
        "Europa",
        (69, 171, 411),
        [2, 4, 8, 13, 17, 21, 23, 23, 18, 13, 7, 3],
        2, 5, 4, 4, 5
    ),

    land(
        "Österreich",
        "Europa",
        (67, 169, 426),
        [0, 2, 7, 12, 17, 20, 22, 22, 17, 12, 5, 1],
        1, 5, 4, 5, 3
    ),

    land(
        "Schweiz",
        "Europa",
        (123, 296, 695),
        [0, 2, 6, 10, 15, 19, 22, 21, 17, 11, 5, 1],
        1, 4, 4, 5, 3
    ),

    land(
        "Island",
        "Europa",
        (94, 218, 505),
        [1, 1, 2, 4, 7, 10, 12, 11, 8, 5, 3, 1],
        1, 3, 3, 5, 2
    ),

    land(
        "Norwegen",
        "Europa",
        (47, 113, 278),
        [-1, 0, 3, 7, 12, 16, 18, 17, 13, 8, 3, 0],
        1, 3, 4, 5, 2
    ),

    land(
        "Schweden",
        "Europa",
        (62, 151, 351),
        [-2, -1, 3, 8, 14, 18, 21, 20, 15, 9, 4, 0],
        2, 4, 4, 5, 3
    ),

    land(
        "Dänemark",
        "Europa",
        (87, 205, 480),
        [2, 2, 5, 9, 14, 17, 20, 20, 16, 11, 7, 4],
        2, 4, 5, 4, 3
    ),

    land(
        "Irland",
        "Europa",
        (65, 162, 400),
        [6, 6, 8, 10, 13, 16, 18, 18, 15, 11, 8, 6],
        2, 5, 4, 5, 4
    ),

    land(
        "Vereinigtes Königreich",
        "Europa",
        (79, 203, 522),
        [5, 6, 8, 11, 14, 17, 20, 19, 16, 12, 8, 6],
        2, 5, 5, 4, 5
    ),

    land(
        "Tschechien",
        "Europa",
        (50, 120, 291),
        [1, 3, 8, 13, 18, 21, 23, 22, 17, 12, 6, 2],
        1, 5, 4, 4, 4
    ),

    land(
        "Polen",
        "Europa",
        (26, 66, 172),
        [-1, 1, 6, 12, 17, 20, 23, 22, 17, 11, 5, 1],
        2, 5, 4, 4, 4
    ),

    land(
        "Ungarn",
        "Europa",
        (38, 97, 249),
        [1, 4, 9, 15, 20, 24, 27, 27, 21, 15, 8, 3],
        1, 5, 5, 3, 5
    ),

    land(
        "Slowenien",
        "Europa",
        (44, 104, 220),
        [1, 3, 8, 12, 17, 21, 23, 22, 18, 13, 7, 3],
        2, 4, 4, 5, 2
    ),

    land(
        "Albanien",
        "Europa",
        (42, 102, 248),
        [7, 9, 13, 17, 21, 26, 29, 29, 25, 20, 14, 9],
        5, 4, 4, 5, 3
    ),

    land(
        "Montenegro",
        "Europa",
        (50, 123, 286),
        [8, 9, 13, 17, 22, 26, 29, 29, 24, 19, 14, 10],
        5, 4, 4, 5, 3
    ),

    land(
        "Malta",
        "Europa",
        (58, 133, 263),
        [13, 13, 15, 18, 22, 26, 29, 29, 26, 23, 18, 15],
        5, 4, 4, 3, 4
    ),

    land(
        "Zypern",
        "Europa",
        (54, 125, 260),
        [12, 13, 16, 20, 24, 28, 31, 31, 28, 24, 19, 14],
        5, 4, 4, 4, 4
    ),


    # ========================================================
    # AUSSERHALB EUROPAS
    # ========================================================

    land(
        "Thailand",
        "Ausserhalb Europas",
        (29, 80, 242),
        [28, 29, 30, 30, 29, 29, 28, 28, 28, 28, 28, 27],
        5, 5, 5, 5, 5
    ),

    land(
        "Vietnam",
        "Ausserhalb Europas",
        (21, 54, 152),
        [21, 22, 24, 27, 29, 30, 30, 29, 28, 26, 24, 21],
        5, 5, 5, 5, 4
    ),

    land(
        "Indonesien",
        "Ausserhalb Europas",
        (19, 54, 164),
        [27, 27, 27, 28, 28, 27, 27, 27, 27, 28, 28, 27],
        5, 4, 5, 5, 4
    ),

    land(
        "Japan",
        "Ausserhalb Europas",
        (45, 113, 286),
        [5, 6, 10, 15, 20, 23, 27, 28, 24, 18, 13, 8],
        3, 5, 5, 5, 4
    ),

    land(
        "Südkorea",
        "Ausserhalb Europas",
        (41, 103, 263),
        [-1, 1, 6, 13, 18, 23, 26, 27, 22, 15, 7, 1],
        3, 5, 5, 4, 5
    ),

    land(
        "Philippinen",
        "Ausserhalb Europas",
        (22, 58, 151),
        [27, 27, 28, 29, 29, 28, 28, 28, 28, 28, 28, 27],
        5, 4, 4, 5, 4
    ),

    land(
        "Sri Lanka",
        "Ausserhalb Europas",
        (17, 46, 138),
        [27, 28, 28, 29, 29, 28, 28, 28, 28, 27, 27, 27],
        5, 5, 5, 5, 3
    ),

    land(
        "Malaysia",
        "Ausserhalb Europas",
        (31, 86, 267),
        [27, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 27],
        5, 4, 5, 5, 4
    ),

    land(
        "Singapur",
        "Ausserhalb Europas",
        (58, 151, 410),
        [27, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 27],
        2, 5, 5, 2, 5
    ),

    land(
        "Indien",
        "Ausserhalb Europas",
        (12, 33, 92),
        [20, 23, 28, 32, 34, 33, 31, 30, 30, 28, 24, 21],
        3, 5, 5, 5, 4
    ),

    land(
        "Nepal",
        "Ausserhalb Europas",
        (12, 32, 97),
        [7, 9, 14, 18, 21, 23, 24, 24, 22, 18, 13, 9],
        1, 5, 4, 5, 2
    ),

    land(
        "Marokko",
        "Ausserhalb Europas",
        (28, 74, 199),
        [13, 14, 17, 19, 22, 26, 29, 29, 26, 22, 17, 14],
        3, 5, 5, 4, 3
    ),

    land(
        "Ägypten",
        "Ausserhalb Europas",
        (13, 31, 72),
        [18, 20, 23, 27, 31, 34, 35, 35, 33, 29, 24, 20],
        5, 5, 4, 4, 3
    ),

    land(
        "Südafrika",
        "Ausserhalb Europas",
        (39, 99, 255),
        [23, 23, 22, 19, 17, 15, 15, 16, 18, 20, 21, 23],
        4, 4, 5, 5, 4
    ),

    land(
        "Tansania",
        "Ausserhalb Europas",
        (35, 90, 247),
        [26, 26, 26, 25, 24, 23, 22, 23, 24, 25, 25, 26],
        5, 4, 4, 5, 2
    ),

    land(
        "Kenia",
        "Ausserhalb Europas",
        (49, 116, 248),
        [24, 25, 25, 24, 23, 22, 21, 21, 23, 24, 23, 24],
        4, 4, 4, 5, 3
    ),

    land(
        "Mexiko",
        "Ausserhalb Europas",
        (44, 123, 377),
        [22, 23, 25, 27, 28, 29, 29, 29, 28, 26, 24, 23],
        5, 5, 5, 4, 5
    ),

    land(
        "Costa Rica",
        "Ausserhalb Europas",
        (50, 126, 314),
        [27, 28, 28, 28, 27, 27, 27, 27, 27, 26, 26, 27],
        5, 3, 4, 5, 3
    ),

    land(
        "Kolumbien",
        "Ausserhalb Europas",
        (20, 55, 175),
        [24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24],
        4, 5, 5, 5, 5
    ),

    land(
        "Brasilien",
        "Ausserhalb Europas",
        (31, 80, 224),
        [27, 27, 26, 24, 22, 21, 21, 22, 22, 23, 25, 26],
        5, 5, 5, 5, 5
    ),

    land(
        "Peru",
        "Ausserhalb Europas",
        (24, 65, 193),
        [19, 19, 19, 18, 17, 16, 16, 17, 18, 19, 19, 19],
        2, 5, 5, 5, 3
    ),

    land(
        "Argentinien",
        "Ausserhalb Europas",
        (23, 54, 110),
        [25, 24, 22, 18, 14, 11, 11, 13, 16, 19, 22, 24],
        4, 5, 5, 5, 5
    ),

    land(
        "Vereinigte Staaten",
        "Ausserhalb Europas",
        (100, 268, 766),
        [5, 7, 11, 16, 21, 26, 29, 28, 24, 18, 12, 7],
        4, 5, 5, 5, 5
    ),

    land(
        "Kanada",
        "Ausserhalb Europas",
        (59, 163, 492),
        [-5, -3, 2, 8, 14, 19, 22, 21, 16, 10, 3, -2],
        2, 4, 4, 5, 3
    ),

    land(
        "Australien",
        "Ausserhalb Europas",
        (60, 157, 415),
        [25, 25, 23, 20, 17, 14, 13, 14, 16, 19, 22, 24],
        5, 4, 5, 5, 5
    )
]


# ============================================================
# 7. MONATE
# ============================================================

# Monatsnamen in richtiger Reihenfolge.
monate = [
    "Januar",
    "Februar",
    "März",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Dezember"
]


# ============================================================
# 8. EINGABEN
# ============================================================

st.header("1. Deine Reise")

# Drei übersichtliche Spalten.
col1, col2, col3 = st.columns(3)


# ------------------------------------------------------------
# REISEZEIT
# ------------------------------------------------------------

with col1:

    # Reisemonat auswählen.
    monat = st.selectbox(
        "📅 Reisemonat",
        monate
    )

    # Reisedauer auswählen.
    tage = st.slider(
        "🗓️ Reisedauer",
        min_value=3,
        max_value=30,
        value=10
    )


# ------------------------------------------------------------
# BUDGET
# ------------------------------------------------------------

with col2:

    # Genaues Maximalbudget eingeben.
    max_budget = st.number_input(
        "💰 Maximalbudget pro Person",
        min_value=100,
        max_value=50000,
        value=1500,
        step=100
    )

    # Budget optional als harte Grenze verwenden.
    budget_muss = st.checkbox(
        "Budget darf nicht überschritten werden",
        value=True
    )


# ------------------------------------------------------------
# REGION
# ------------------------------------------------------------

with col3:

    # Region auswählen.
    region = st.selectbox(
        "🌍 Region",
        [
            "Egal",
            "Europa",
            "Ausserhalb Europas"
        ]
    )

    # Wunschtemperatur.
    wunschtemperatur = st.slider(
        "🌡️ Wunschtemperatur",
        min_value=-5,
        max_value=35,
        value=25
    )


# ============================================================
# 9. REISESTIL
# ============================================================

st.subheader("2. Wie möchtest du reisen?")

# Einfache horizontale Auswahl.
reisestil = st.radio(
    "Reisestil",
    [
        "Sparsam",
        "Komfort",
        "Luxuriös"
    ],
    horizontal=True
)

# Kurze Erklärung unter der Auswahl.
if reisestil == "Sparsam":

    st.caption(
        "Einfachere Unterkünfte, günstiger essen und preisbewusst reisen."
    )

elif reisestil == "Komfort":

    st.caption(
        "Mittelklasse-Unterkünfte, Restaurants und mehr bezahlte Aktivitäten."
    )

else:

    st.caption(
        "Gehobene Unterkünfte, Restaurants und deutlich höheres Reisebudget."
    )


# ============================================================
# 10. INTERESSEN
# ============================================================

st.subheader("3. Was ist dir wichtig?")

st.caption(
    "1 = unwichtig · 5 = sehr wichtig"
)

# Fünf Spalten für die Interessen.
i1, i2, i3, i4, i5 = st.columns(5)


with i1:

    # Wichtigkeit Strand.
    strand_wichtig = st.slider(
        "🏖️ Strand",
        1,
        5,
        3
    )

    # Strand kann zusätzlich zwingend sein.
    strand_muss = st.checkbox(
        "Strand muss vorhanden sein"
    )


with i2:

    # Wichtigkeit Kultur.
    kultur_wichtig = st.slider(
        "🏛️ Kultur",
        1,
        5,
        3
    )


with i3:

    # Wichtigkeit Essen.
    essen_wichtig = st.slider(
        "🍜 Essen",
        1,
        5,
        3
    )


with i4:

    # Wichtigkeit Natur.
    natur_wichtig = st.slider(
        "🌿 Natur",
        1,
        5,
        3
    )


with i5:

    # Wichtigkeit Nightlife.
    nightlife_wichtig = st.slider(
        "🎉 Nightlife",
        1,
        5,
        2
    )


# Kleiner Abstand vor dem Button.
st.write("")


# ============================================================
# 11. SUCHE STARTEN
# ============================================================

if st.button(
    "✈️ Reiseziele finden",
    type="primary"
):

    # --------------------------------------------------------
    # MONATSINDEX
    # --------------------------------------------------------

    # Januar = Position 0, Februar = 1 usw.
    monats_index = monate.index(monat)


    # --------------------------------------------------------
    # KANDIDATENLISTE
    # --------------------------------------------------------

    # Hier sammeln wir alle passenden Länder.
    kandidaten = []


    # Alle Länder einzeln prüfen.
    for ziel in reiseziele:

        # ----------------------------------------------------
        # REGION
        # ----------------------------------------------------

        # Falls Nutzer eine Region gewählt hat,
        # muss das Land dieser Region entsprechen.
        if region != "Egal":

            if ziel["region"] != region:

                continue


        # ----------------------------------------------------
        # STRAND ALS MUSS-KRITERIUM
        # ----------------------------------------------------

        # Wenn Strand zwingend ist,
        # behalten wir nur Länder mit Strandbewertung 4 oder 5.
        if strand_muss:

            if ziel["strand"] < 4:

                continue


        # ----------------------------------------------------
        # GESCHÄTZTE KOSTEN
        # ----------------------------------------------------

        # Tagesbudget des gewählten Reisestils auswählen.
        kosten_pro_tag = ziel["budgets"][reisestil]

        # Geschätzte Kosten für die ganze Reise.
        geschaetzte_kosten = (
            kosten_pro_tag * tage
        )


        # ----------------------------------------------------
        # BUDGET ALS MUSS-KRITERIUM
        # ----------------------------------------------------

        # Falls Budget zwingend ist,
        # werden zu teure Länder ausgeschlossen.
        if budget_muss:

            if geschaetzte_kosten > max_budget:

                continue


        # ----------------------------------------------------
        # TEMPERATUR
        # ----------------------------------------------------

        # Temperatur des gewählten Monats laden.
        temperatur = ziel["temperaturen"][
            monats_index
        ]


        # ----------------------------------------------------
        # MATCH-BERECHNUNG
        # ----------------------------------------------------
        #
        # Wichtig:
        #
        # Die Slider beschreiben jetzt wirklich die
        # WICHTIGKEIT eines Themas.
        #
        # Beispiel:
        #
        # Essen = 1
        # -> Essen beeinflusst das Ergebnis gar nicht.
        #
        # Essen = 5
        # -> Essen beeinflusst das Ergebnis maximal.
        #
        #
        # Gewicht:
        #
        # 1 -> 0.00
        # 2 -> 0.25
        # 3 -> 0.50
        # 4 -> 0.75
        # 5 -> 1.00
        #
        #
        # Das Länder-Rating wird durch 5 geteilt:
        #
        # Rating 5 = 100 % Eignung
        # Rating 4 = 80 %
        # Rating 3 = 60 %
        # usw.
        # ----------------------------------------------------


        # Wichtigkeit von Strand in Gewicht umwandeln.
        gewicht_strand = (
            strand_wichtig - 1
        ) / 4

        # Wichtigkeit Kultur.
        gewicht_kultur = (
            kultur_wichtig - 1
        ) / 4

        # Wichtigkeit Essen.
        gewicht_essen = (
            essen_wichtig - 1
        ) / 4

        # Wichtigkeit Natur.
        gewicht_natur = (
            natur_wichtig - 1
        ) / 4

        # Wichtigkeit Nightlife.
        gewicht_nightlife = (
            nightlife_wichtig - 1
        ) / 4


        # ----------------------------------------------------
        # TEMPERATUR-MATCH
        # ----------------------------------------------------

        # Absolute Differenz zur Wunschtemperatur.
        temperatur_unterschied = abs(
            temperatur
            - wunschtemperatur
        )

        # Temperaturmatch berechnen.
        #
        # Gleiche Temperatur = 100 %
        #
        # 20 °C oder mehr Abweichung = 0 %
        temperatur_match = max(
            0,
            1 - temperatur_unterschied / 20
        )


        # ----------------------------------------------------
        # AKTIVITÄTS-MATCHES
        # ----------------------------------------------------

        # Strandrating in Wert zwischen 0 und 1 umwandeln.
        strand_match = ziel["strand"] / 5

        # Kulturrating umwandeln.
        kultur_match = ziel["kultur"] / 5

        # Essen umwandeln.
        essen_match = ziel["essen"] / 5

        # Natur umwandeln.
        natur_match = ziel["natur"] / 5

        # Nightlife umwandeln.
        nightlife_match = ziel["nightlife"] / 5


        # ----------------------------------------------------
        # BUDGET-MATCH
        # ----------------------------------------------------
        #
        # Wenn das Land innerhalb des Budgets liegt,
        # gibt es 100 % Budget-Match.
        #
        # Ein günstigeres Land wird NICHT bestraft.
        #
        # Wenn Budget nicht zwingend ist und überschritten wird,
        # sinkt der Budget-Match.
        # ----------------------------------------------------

        if geschaetzte_kosten <= max_budget:

            budget_match = 1

        else:

            # Relative Überschreitung berechnen.
            ueberschreitung = (
                geschaetzte_kosten
                - max_budget
            ) / max_budget

            # Match reduzieren.
            budget_match = max(
                0,
                1 - ueberschreitung
            )


        # ----------------------------------------------------
        # GESAMTMATCH
        # ----------------------------------------------------
        #
        # Temperatur hat immer Gewicht 1.
        #
        # Budget hat Gewicht 1.
        #
        # Interessen werden entsprechend der Nutzereingabe
        # unterschiedlich stark gewichtet.
        # ----------------------------------------------------

        punkte = (
            temperatur_match * 1
            + budget_match * 1
            + strand_match * gewicht_strand
            + kultur_match * gewicht_kultur
            + essen_match * gewicht_essen
            + natur_match * gewicht_natur
            + nightlife_match * gewicht_nightlife
        )


        # Gesamtgewicht berechnen.
        gesamtgewicht = (
            1
            + 1
            + gewicht_strand
            + gewicht_kultur
            + gewicht_essen
            + gewicht_natur
            + gewicht_nightlife
        )


        # Durchschnitt zwischen 0 und 1 berechnen.
        match = (
            punkte
            / gesamtgewicht
        )


        # In Prozent umwandeln.
        match_prozent = round(
            match * 100
        )


        # ----------------------------------------------------
        # ERGEBNIS SPEICHERN
        # ----------------------------------------------------

        kandidaten.append(
            {
                **ziel,

                "temperatur": temperatur,

                "kosten_pro_tag": kosten_pro_tag,

                "geschaetzte_kosten": geschaetzte_kosten,

                "match": match_prozent,

                "details": [
                    {
                        "Kriterium": "Temperatur",
                        "Passung": f"{round(temperatur_match * 100)} %"
                    },
                    {
                        "Kriterium": "Budget",
                        "Passung": f"{round(budget_match * 100)} %"
                    },
                    {
                        "Kriterium": "Strand",
                        "Wichtigkeit": strand_wichtig,
                        "Angebot": f"{ziel['strand']}/5"
                    },
                    {
                        "Kriterium": "Kultur",
                        "Wichtigkeit": kultur_wichtig,
                        "Angebot": f"{ziel['kultur']}/5"
                    },
                    {
                        "Kriterium": "Essen",
                        "Wichtigkeit": essen_wichtig,
                        "Angebot": f"{ziel['essen']}/5"
                    },
                    {
                        "Kriterium": "Natur",
                        "Wichtigkeit": natur_wichtig,
                        "Angebot": f"{ziel['natur']}/5"
                    },
                    {
                        "Kriterium": "Nightlife",
                        "Wichtigkeit": nightlife_wichtig,
                        "Angebot": f"{ziel['nightlife']}/5"
                    }
                ]
            }
        )


    # ========================================================
    # 12. ERGEBNISSE SORTIEREN
    # ========================================================

    # Höchster Match zuerst.
    kandidaten = sorted(
        kandidaten,
        key=lambda x: x["match"],
        reverse=True
    )


    # Nur fünf beste Ergebnisse.
    kandidaten = kandidaten[:5]


    # ========================================================
    # 13. KEINE RESULTATE
    # ========================================================

    if len(kandidaten) == 0:

        st.warning(
            """
            Kein Reiseziel erfüllt aktuell alle deine
            zwingenden Kriterien.

            Versuche zum Beispiel:
            - Budget erhöhen
            - Region auf "Egal" stellen
            - Strand nicht als zwingend auswählen
            """
        )

        st.stop()


    # ========================================================
    # 14. RESULTATE ANZEIGEN
    # ========================================================

    st.divider()

    st.header("✨ Deine besten Matches")


    # Ergebnisse einzeln anzeigen.
    for position, ziel in enumerate(
        kandidaten,
        start=1
    ):

        # Native Streamlit-Karte.
        with st.container(border=True):

            # Ländername.
            st.subheader(
                f"{position}. {ziel['land']}"
            )

            # Match.
            st.write(
                f"**{ziel['match']} % Match**"
            )

            # Match-Balken.
            st.progress(
                ziel["match"] / 100
            )


            # ------------------------------------------------
            # HAUPTINFORMATIONEN
            # ------------------------------------------------

            c1, c2, c3 = st.columns(3)


            with c1:

                # Temperatur.
                st.metric(
                    f"🌡️ Ø {monat}",
                    f"{ziel['temperatur']} °C"
                )


            with c2:

                # Geschätzte Gesamtkosten.
                st.metric(
                    "💰 Geschätzte Kosten",
                    f"CHF {ziel['geschaetzte_kosten']}"
                )


            with c3:

                # Geschätzte Kosten pro Tag.
                st.metric(
                    f"💵 {reisestil} pro Tag",
                    f"CHF {ziel['kosten_pro_tag']}"
                )


            # ------------------------------------------------
            # BUDGETSPANNE
            # ------------------------------------------------

            # Kleine, unaufdringliche Übersicht.
            st.caption(
                "Budgetspanne pro Tag: "
                f"Sparsam CHF {ziel['budgets']['Sparsam']} · "
                f"Komfort CHF {ziel['budgets']['Komfort']} · "
                f"Luxuriös CHF {ziel['budgets']['Luxuriös']}"
            )


            # ------------------------------------------------
            # AKTIVITÄTEN
            # ------------------------------------------------

            st.markdown(
                "**Was dich dort erwartet:**"
            )

            a1, a2, a3, a4, a5 = st.columns(5)


            with a1:

                st.write(
                    f"🏖️ **Strand**\n\n{ziel['strand']}/5"
                )


            with a2:

                st.write(
                    f"🏛️ **Kultur**\n\n{ziel['kultur']}/5"
                )


            with a3:

                st.write(
                    f"🍜 **Essen**\n\n{ziel['essen']}/5"
                )


            with a4:

                st.write(
                    f"🌿 **Natur**\n\n{ziel['natur']}/5"
                )


            with a5:

                st.write(
                    f"🎉 **Nightlife**\n\n{ziel['nightlife']}/5"
                )


            # ------------------------------------------------
            # BUDGETSTATUS
            # ------------------------------------------------

            # Wenn innerhalb des Budgets.
            if ziel["geschaetzte_kosten"] <= max_budget:

                # Verbleibendes Budget berechnen.
                rest = (
                    max_budget
                    - ziel["geschaetzte_kosten"]
                )

                st.success(
                    f"✓ Geschätzte Kosten liegen im Budget. "
                    f"Ca. CHF {rest} bleiben übrig."
                )

            else:

                # Überschreitung berechnen.
                zu_teuer = (
                    ziel["geschaetzte_kosten"]
                    - max_budget
                )

                st.warning(
                    f"Geschätzte Kosten liegen ca. "
                    f"CHF {zu_teuer} über deinem Budget."
                )


            # ------------------------------------------------
            # MATCH ERKLÄREN
            # ------------------------------------------------

            # Erklärung ist standardmässig geschlossen,
            # damit die App nicht überladen wirkt.
            with st.expander(
                f"Warum {ziel['match']} % Match?"
            ):

                st.write(
                    """
                    Der Match berücksichtigt deine
                    Wunschtemperatur, dein Budget und wie wichtig
                    dir Strand, Kultur, Essen, Natur und Nightlife sind.
                    """
                )

                # Einfache Tabelle anzeigen.
                st.table(
                    ziel["details"]
                )
