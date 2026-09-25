# ============================================================
# TRAVELMATCH - EINFACHER REISEZIEL-RECOMMENDER
# ============================================================
#
# Ziel der App:
# Die App empfiehlt passende Reiseziele anhand von:
# - Reisemonat
# - Reisedauer
# - Budget
# - Region
# - gewünschter Temperatur
# - Interessen
#
# Technische Idee:
# Für jedes Land wird berechnet, wie ähnlich es den
# Nutzerwünschen ist.
#
# Je kleiner die berechnete Distanz, desto besser passt
# das Land zum Nutzerprofil.
#
# Das Verfahren basiert auf dem Prinzip von
# "Nearest Neighbors".
#
# WICHTIG:
# Die Reisedaten sind vereinfachte Beispieldaten.
# Sie dienen nur zu Demonstrationszwecken.
# ============================================================


# ------------------------------------------------------------
# 1. BIBLIOTHEKEN IMPORTIEREN
# ------------------------------------------------------------

# Streamlit wird für die Weboberfläche verwendet.
import streamlit as st

# pandas wird verwendet, um die Reisedaten als Tabelle
# zu verarbeiten.
import pandas as pd

# math wird für mathematische Berechnungen verwendet.
import math


# ------------------------------------------------------------
# 2. STREAMLIT-SEITE EINRICHTEN
# ------------------------------------------------------------

st.set_page_config(
    page_title="TravelMatch",
    page_icon="🌍",
    layout="wide"
)


# ------------------------------------------------------------
# 3. TITEL
# ------------------------------------------------------------

st.title("🌍 TravelMatch")

st.write(
    """
    Finde Reiseziele, die zu deinem Budget, deinem Reisemonat,
    deiner gewünschten Temperatur und deinen Interessen passen.
    """
)


# ------------------------------------------------------------
# 4. REISEZIEL-DATEN
# ------------------------------------------------------------
#
# Jede Zeile enthält:
#
# Land
# Region
# geschätzte Tageskosten
# Temperaturen Januar bis Dezember
# Strand-Bewertung
# Kultur-Bewertung
# Essen-Bewertung
# Natur-Bewertung
# Nightlife-Bewertung
#
# Bewertungen:
# 1 = wenig geeignet
# 5 = sehr gut geeignet
#
# Hinweis:
# Die Werte sind vereinfachte Beispieldaten.
# ------------------------------------------------------------

destinations = [

    # ==========================
    # EUROPA
    # ==========================

    ["Portugal", "Europe", 90, 15, 16, 18, 19, 22, 25, 28, 28, 26, 22, 18, 16, 5, 4, 5, 4, 4],
    ["Spain", "Europe", 100, 12, 13, 16, 18, 22, 27, 30, 30, 26, 21, 16, 13, 5, 5, 5, 4, 5],
    ["Italy", "Europe", 110, 8, 10, 13, 17, 21, 25, 28, 28, 24, 19, 13, 9, 4, 5, 5, 4, 4],
    ["Greece", "Europe", 95, 10, 11, 14, 18, 23, 28, 31, 31, 27, 22, 17, 12, 5, 5, 4, 4, 4],
    ["Croatia", "Europe", 90, 7, 9, 13, 17, 22, 26, 29, 29, 24, 19, 13, 9, 5, 4, 4, 5, 3],
    ["France", "Europe", 125, 6, 7, 11, 14, 18, 22, 25, 25, 21, 16, 10, 7, 4, 5, 5, 4, 4],
    ["Netherlands", "Europe", 120, 5, 6, 9, 13, 17, 20, 22, 22, 19, 14, 9, 6, 2, 5, 4, 3, 4],
    ["Belgium", "Europe", 115, 5, 6, 9, 12, 16, 19, 21, 21, 18, 14, 9, 6, 2, 5, 5, 3, 4],
    ["Germany", "Europe", 110, 2, 4, 8, 13, 17, 21, 23, 23, 18, 13, 7, 3, 2, 5, 4, 4, 4],
    ["Austria", "Europe", 115, 0, 2, 7, 12, 17, 20, 22, 22, 17, 12, 5, 1, 1, 5, 4, 5, 2],
    ["Switzerland", "Europe", 180, 0, 2, 6, 10, 15, 19, 22, 21, 17, 11, 5, 1, 1, 4, 4, 5, 2],
    ["Iceland", "Europe", 180, 1, 1, 2, 4, 7, 10, 12, 11, 8, 5, 3, 1, 1, 3, 3, 5, 1],
    ["Norway", "Europe", 165, -1, 0, 3, 7, 12, 16, 18, 17, 13, 8, 3, 0, 1, 3, 4, 5, 2],
    ["Sweden", "Europe", 135, -2, -1, 3, 8, 14, 18, 21, 20, 15, 9, 4, 0, 2, 4, 4, 5, 3],
    ["Denmark", "Europe", 145, 2, 2, 5, 9, 14, 17, 20, 20, 16, 11, 7, 4, 2, 4, 5, 4, 3],
    ["Ireland", "Europe", 120, 6, 6, 8, 10, 13, 16, 18, 18, 15, 11, 8, 6, 2, 5, 4, 5, 4],
    ["United Kingdom", "Europe", 130, 5, 6, 8, 11, 14, 17, 20, 19, 16, 12, 8, 6, 2, 5, 5, 4, 5],
    ["Czech Republic", "Europe", 75, 1, 3, 8, 13, 18, 21, 23, 22, 17, 12, 6, 2, 1, 5, 4, 4, 4],
    ["Poland", "Europe", 65, -1, 1, 6, 12, 17, 20, 23, 22, 17, 11, 5, 1, 2, 5, 4, 4, 4],
    ["Hungary", "Europe", 65, 1, 4, 9, 15, 20, 24, 27, 27, 21, 15, 8, 3, 1, 5, 5, 3, 5],
    ["Slovenia", "Europe", 85, 1, 3, 8, 12, 17, 21, 23, 22, 18, 13, 7, 3, 2, 4, 4, 5, 2],
    ["Albania", "Europe", 60, 7, 9, 13, 17, 21, 26, 29, 29, 25, 20, 14, 9, 5, 4, 4, 5, 3],
    ["Montenegro", "Europe", 70, 8, 9, 13, 17, 22, 26, 29, 29, 24, 19, 14, 10, 5, 4, 4, 5, 3],
    ["Malta", "Europe", 95, 13, 13, 15, 18, 22, 26, 29, 29, 26, 23, 18, 15, 5, 4, 4, 3, 4],
    ["Cyprus", "Europe", 95, 12, 13, 16, 20, 24, 28, 31, 31, 28, 24, 19, 14, 5, 4, 4, 4, 4],

    # ==========================
    # AUSSERHALB EUROPAS
    # ==========================

    ["Thailand", "Outside Europe", 55, 28, 29, 30, 30, 29, 29, 28, 28, 28, 28, 28, 27, 5, 5, 5, 5, 5],
    ["Vietnam", "Outside Europe", 50, 21, 22, 24, 27, 29, 30, 30, 29, 28, 26, 24, 21, 5, 5, 5, 5, 4],
    ["Indonesia", "Outside Europe", 55, 27, 27, 27, 28, 28, 27, 27, 27, 27, 28, 28, 27, 5, 4, 5, 5, 4],
    ["Japan", "Outside Europe", 120, 5, 6, 10, 15, 20, 23, 27, 28, 24, 18, 13, 8, 3, 5, 5, 5, 4],
    ["South Korea", "Outside Europe", 100, -1, 1, 6, 13, 18, 23, 26, 27, 22, 15, 7, 1, 3, 5, 5, 4, 5],
    ["Philippines", "Outside Europe", 60, 27, 27, 28, 29, 29, 28, 28, 28, 28, 28, 28, 27, 5, 4, 4, 5, 4],
    ["Sri Lanka", "Outside Europe", 50, 27, 28, 28, 29, 29, 28, 28, 28, 28, 27, 27, 27, 5, 5, 5, 5, 3],
    ["Malaysia", "Outside Europe", 60, 27, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 27, 5, 4, 5, 5, 4],
    ["Singapore", "Outside Europe", 140, 27, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 27, 2, 5, 5, 2, 5],
    ["India", "Outside Europe", 45, 20, 23, 28, 32, 34, 33, 31, 30, 30, 28, 24, 21, 3, 5, 5, 5, 4],
    ["Nepal", "Outside Europe", 40, 7, 9, 14, 18, 21, 23, 24, 24, 22, 18, 13, 9, 1, 5, 4, 5, 2],
    ["Morocco", "Outside Europe", 60, 13, 14, 17, 19, 22, 26, 29, 29, 26, 22, 17, 14, 3, 5, 5, 4, 3],
    ["Egypt", "Outside Europe", 55, 18, 20, 23, 27, 31, 34, 35, 35, 33, 29, 24, 20, 5, 5, 4, 4, 3],
    ["South Africa", "Outside Europe", 80, 23, 23, 22, 19, 17, 15, 15, 16, 18, 20, 21, 23, 4, 4, 5, 5, 4],
    ["Tanzania", "Outside Europe", 70, 26, 26, 26, 25, 24, 23, 22, 23, 24, 25, 25, 26, 5, 4, 4, 5, 2],
    ["Kenya", "Outside Europe", 70, 24, 25, 25, 24, 23, 22, 21, 21, 23, 24, 23, 24, 4, 4, 4, 5, 3],
    ["Mexico", "Outside Europe", 75, 22, 23, 25, 27, 28, 29, 29, 29, 28, 26, 24, 23, 5, 5, 5, 4, 5],
    ["Costa Rica", "Outside Europe", 90, 27, 28, 28, 28, 27, 27, 27, 27, 27, 26, 26, 27, 5, 3, 4, 5, 3],
    ["Colombia", "Outside Europe", 55, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 4, 5, 5, 5, 5],
    ["Brazil", "Outside Europe", 75, 27, 27, 26, 24, 22, 21, 21, 22, 22, 23, 25, 26, 5, 5, 5, 5, 5],
    ["Peru", "Outside Europe", 55, 19, 19, 19, 18, 17, 16, 16, 17, 18, 19, 19, 19, 2, 5, 5, 5, 3],
    ["Argentina", "Outside Europe", 75, 25, 24, 22, 18, 14, 11, 11, 13, 16, 19, 22, 24, 4, 5, 5, 5, 5],
    ["USA", "Outside Europe", 150, 5, 7, 11, 16, 21, 26, 29, 28, 24, 18, 12, 7, 4, 5, 5, 5, 5],
    ["Canada", "Outside Europe", 140, -5, -3, 2, 8, 14, 19, 22, 21, 16, 10, 3, -2, 2, 4, 4, 5, 3],
    ["Australia", "Outside Europe", 130, 25, 25, 23, 20, 17, 14, 13, 14, 16, 19, 22, 24, 5, 4, 5, 5, 5]
]


# ------------------------------------------------------------
# 5. SPALTENNAMEN DEFINIEREN
# ------------------------------------------------------------

columns = [
    "country",
    "region",
    "daily_cost",
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
    "beach",
    "culture",
    "food",
    "nature",
    "nightlife"
]


# ------------------------------------------------------------
# 6. DATEN ALS TABELLE SPEICHERN
# ------------------------------------------------------------

df = pd.DataFrame(
    destinations,
    columns=columns
)


# ------------------------------------------------------------
# 7. NUTZEREINGABEN
# ------------------------------------------------------------

st.header("1. Reisedaten")

col1, col2 = st.columns(2)

months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec"
]


with col1:

    month = st.selectbox(
        "Wann möchtest du reisen?",
        months
    )

    days = st.slider(
        "Wie viele Tage möchtest du reisen?",
        min_value=3,
        max_value=30,
        value=10
    )

    budget = st.slider(
        "Gesamtbudget pro Person in CHF",
        min_value=300,
        max_value=5000,
        value=1500,
        step=100
    )


with col2:

    region = st.selectbox(
        "Welche Region kommt infrage?",
        [
            "Egal",
            "Europe",
            "Outside Europe"
        ]
    )

    desired_temperature = st.slider(
        "Welche Temperatur möchtest du ungefähr?",
        min_value=-5,
        max_value=35,
        value=25,
        unit=" °C"
    )


# ------------------------------------------------------------
# 8. INTERESSEN
# ------------------------------------------------------------

st.header("2. Was möchtest du im Urlaub machen?")

st.write(
    "1 = unwichtig | 5 = sehr wichtig"
)

interest_col1, interest_col2, interest_col3 = st.columns(3)


with interest_col1:

    beach = st.slider(
        "🏖️ Strand",
        1,
        5,
        3
    )

    nature = st.slider(
        "🌿 Natur",
        1,
        5,
        3
    )


with interest_col2:

    culture = st.slider(
        "🏛️ Kultur",
        1,
        5,
        3
    )

    food = st.slider(
        "🍜 Essen",
        1,
        5,
        3
    )


with interest_col3:

    nightlife = st.slider(
        "🎉 Nightlife",
        1,
        5,
        2
    )


# ------------------------------------------------------------
# 9. BUTTON STARTET DIE EMPFEHLUNG
# ------------------------------------------------------------

if st.button(
    "✈️ Passende Reiseziele finden",
    type="primary"
):

    # --------------------------------------------------------
    # 9.1 DATEN KOPIEREN
    # --------------------------------------------------------

    filtered_df = df.copy()


    # --------------------------------------------------------
    # 9.2 REGION FILTERN
    # --------------------------------------------------------

    if region == "Europe":

        filtered_df = filtered_df[
            filtered_df["region"] == "Europe"
        ]

    elif region == "Outside Europe":

        filtered_df = filtered_df[
            filtered_df["region"] == "Outside Europe"
        ]


    # --------------------------------------------------------
    # 9.3 TEMPERATUR DES GEWÄHLTEN MONATS
    # --------------------------------------------------------

    filtered_df["temperature"] = filtered_df[month]


    # --------------------------------------------------------
    # 9.4 GESCHÄTZTE KOSTEN VOR ORT
    # --------------------------------------------------------

    filtered_df["estimated_cost"] = (
        filtered_df["daily_cost"] * days
    )


    # --------------------------------------------------------
    # 9.5 USER-PROFIL ERSTELLEN
    # --------------------------------------------------------

    budget_per_day = budget / days

    user_values = {
        "daily_cost": budget_per_day,
        "temperature": desired_temperature,
        "beach": beach,
        "culture": culture,
        "food": food,
        "nature": nature,
        "nightlife": nightlife
    }


    # --------------------------------------------------------
    # 9.6 FEATURES FÜR DEN VERGLEICH
    # --------------------------------------------------------

    features = [
        "daily_cost",
        "temperature",
        "beach",
        "culture",
        "food",
        "nature",
        "nightlife"
    ]


    # --------------------------------------------------------
    # 9.7 STANDARDISIERUNG
    # --------------------------------------------------------
    #
    # Die Features haben verschiedene Grössenordnungen.
    #
    # Beispiel:
    # Tageskosten: 40 bis 180
    # Bewertungen: 1 bis 5
    #
    # Deshalb werden die Werte standardisiert.
    # --------------------------------------------------------

    means = {}
    standard_deviations = {}


    for feature in features:

        values = filtered_df[feature].tolist()

        mean = sum(values) / len(values)

        variance = sum(
            (value - mean) ** 2
            for value in values
        ) / len(values)

        standard_deviation = math.sqrt(
            variance
        )

        # Verhindert Division durch 0
        if standard_deviation == 0:
            standard_deviation = 1

        means[feature] = mean

        standard_deviations[feature] = (
            standard_deviation
        )


    # --------------------------------------------------------
    # 9.8 DISTANZ ZU JEDEM LAND BERECHNEN
    # --------------------------------------------------------
    #
    # Kleine Distanz = hohe Ähnlichkeit.
    #
    # Verwendet wird die euklidische Distanz.
    # --------------------------------------------------------

    results = []


    for index, country in filtered_df.iterrows():

        squared_distance = 0


        for feature in features:

            # Standardisierter Wert des Landes
            country_standardized = (
                country[feature] -
                means[feature]
            ) / standard_deviations[feature]


            # Standardisierter Wert des Nutzers
            user_standardized = (
                user_values[feature] -
                means[feature]
            ) / standard_deviations[feature]


            # Differenz quadrieren
            squared_distance += (
                country_standardized -
                user_standardized
            ) ** 2


        # Quadratwurzel ergibt die euklidische Distanz
        distance = math.sqrt(
            squared_distance
        )


        # Ergebnis speichern
        results.append(
            {
                "index": index,
                "distance": distance
            }
        )


    # --------------------------------------------------------
    # 9.9 LÄNDER NACH ÄHNLICHKEIT SORTIEREN
    # --------------------------------------------------------

    results = sorted(
        results,
        key=lambda x: x["distance"]
    )


    # Nur die fünf besten Ergebnisse anzeigen
    results = results[:5]


    # --------------------------------------------------------
    # 10. ERGEBNISSE ANZEIGEN
    # --------------------------------------------------------

    st.divider()

    st.header(
        "🌎 Deine besten Reiseziele"
    )


    for ranking, item in enumerate(results):

        index = item["index"]

        distance = item["distance"]

        result = filtered_df.loc[index]


        # ----------------------------------------------------
        # MATCH SCORE
        # ----------------------------------------------------
        #
        # Dieser Prozentwert dient nur als verständliche
        # Darstellung der Distanz.
        #
        # Es handelt sich NICHT um eine statistische
        # Wahrscheinlichkeit.
        # ----------------------------------------------------

        match_score = max(
            0,
            min(
                100,
                round(
                    100 - distance * 12
                )
            )
        )


        # ----------------------------------------------------
        # LAND ANZEIGEN
        # ----------------------------------------------------

        st.subheader(
            f"{ranking + 1}. {result['country']}"
        )


        st.progress(
            match_score / 100
        )


        st.write(
            f"**Match Score: {match_score}%**"
        )


        # ----------------------------------------------------
        # KENNZAHLEN
        # ----------------------------------------------------

        result_col1, result_col2, result_col3 = st.columns(3)


        with result_col1:

            st.metric(
                "🌡️ Temperatur",
                f"{result['temperature']} °C"
            )


        with result_col2:

            st.metric(
                "💰 Kosten vor Ort",
                f"CHF {result['estimated_cost']:.0f}"
            )


        with result_col3:

            st.metric(
                "💵 Tageskosten",
                f"CHF {result['daily_cost']:.0f}"
            )


        # ----------------------------------------------------
        # INTERESSEN
        # ----------------------------------------------------

        st.write(
            "**Eignung für Aktivitäten:**"
        )


        st.write(
            f"""
            🏖️ Strand: {result['beach']}/5  
            🏛️ Kultur: {result['culture']}/5  
            🍜 Essen: {result['food']}/5  
            🌿 Natur: {result['nature']}/5  
            🎉 Nightlife: {result['nightlife']}/5
            """
        )


        # ----------------------------------------------------
        # BUDGETPRÜFUNG
        # ----------------------------------------------------

        if result["estimated_cost"] > budget:

            st.warning(
                "⚠️ Die geschätzten Kosten vor Ort "
                "liegen über deinem angegebenen Budget."
            )

        else:

            remaining_budget = (
                budget -
                result["estimated_cost"]
            )

            st.success(
                f"✅ Nach den geschätzten Kosten vor Ort "
                f"bleiben ca. CHF {remaining_budget:.0f} "
                f"für Flug und weitere Ausgaben."
            )


        st.divider()


# ------------------------------------------------------------
# 11. METHODISCHER HINWEIS
# ------------------------------------------------------------

st.caption(
    """
    Methodischer Hinweis:
    Die App verwendet einen similarity-basierten
    Nearest-Neighbor-Ansatz. Dazu werden die Eigenschaften
    der Länder standardisiert und mit dem Nutzerprofil
    verglichen. Die Länder mit der kleinsten euklidischen
    Distanz werden empfohlen. Die verwendeten Reisedaten
    sind vereinfachte Beispieldaten und keine Live-Daten.
    Der Match Score ist keine statistische Wahrscheinlichkeit.
    """
)
