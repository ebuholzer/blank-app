# ============================================================
# TRAVELMATCH
# Reiseziel-Empfehlung mit Similarity-/Nearest-Neighbor-Prinzip
# ============================================================


# ------------------------------------------------------------
# 1. BIBLIOTHEKEN IMPORTIEREN
# ------------------------------------------------------------

# Streamlit wird verwendet, um die Web-App aufzubauen.
import streamlit as st

# math wird für die Berechnung der euklidischen Distanz benötigt.
import math

# json wird benötigt, um die Antwort der Wetter-API zu lesen.
import json

# urlopen ermöglicht den Zugriff auf die Open-Meteo API.
from urllib.request import urlopen

# urlencode wandelt unsere API-Parameter in eine gültige URL um.
from urllib.parse import urlencode


# ============================================================
# 2. SEITE KONFIGURIEREN
# ============================================================

# Grundeinstellungen der Streamlit-Seite.
st.set_page_config(
    # Titel im Browser.
    page_title="TravelMatch",

    # Icon im Browser.
    page_icon="🌍",

    # Breiteres Layout.
    layout="wide"
)


# ============================================================
# 3. ETWAS SCHÖNERES STREAMLIT-DESIGN
# ============================================================
#
# Wir verwenden nur wenig CSS.
#
# Anders als in der vorherigen Version werden die eigentlichen
# Resultate NICHT mehr mit selbst geschriebenem HTML aufgebaut.
#
# Dadurch vermeiden wir, dass Streamlit HTML-Tags als Code anzeigt.
# ============================================================

st.markdown(
    """
    <style>

    /* Begrenzung der maximalen Inhaltsbreite */
    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* Primärer Button */
    div.stButton > button {
        width: 100%;
        min-height: 3.2rem;
        border-radius: 14px;
        font-weight: 700;
        font-size: 1rem;
    }

    /* Etwas mehr Abstand zwischen Überschriften */
    h1, h2, h3 {
        margin-bottom: 0.6rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 4. TITEL
# ============================================================

# Haupttitel der App.
st.title("🌍 TravelMatch")

# Untertitel.
st.markdown(
    """
    ### Wohin soll deine nächste Reise gehen?

    Wähle Budget, Reisezeit, Temperatur und deine Interessen.
    TravelMatch vergleicht deine Wünsche mit 50 Reiseländern.
    """
)

# Kleine Trennlinie.
st.divider()


# ============================================================
# 5. DATENGRUNDLAGE
# ============================================================
#
# Für jedes Land werden folgende Informationen gespeichert:
#
# land:
# Deutscher Ländername.
#
# flagge:
# Länderflagge.
#
# region:
# Europa oder ausserhalb Europas.
#
# ort:
# Repräsentative Destination innerhalb des Landes.
#
# lat / lon:
# Koordinaten dieses Ortes.
#
# Sie werden für historische Wetterdaten verwendet.
#
# kosten:
# Vereinfachtes durchschnittliches Tagesbudget in CHF.
#
# strand / kultur / essen / natur / nightlife:
# Bewertung zwischen 1 und 5.
#
#
# ------------------------------------------------------------
# HERLEITUNG DER AKTIVITÄTSFAKTOREN
# ------------------------------------------------------------
#
# 1 = sehr geringe Eignung
# 2 = eher geringe Eignung
# 3 = mittlere Eignung
# 4 = gute Eignung
# 5 = sehr hohe Eignung
#
# Diese Werte sind im Prototyp heuristisch gesetzt.
#
# Beispiel Thailand:
#
# Strand = 5
# Begründung:
# Thailand besitzt zahlreiche bekannte Strand- und
# Inseldestinationen.
#
# Kultur = 5
# Begründung:
# Tempel, historische Orte und starke kulturelle Angebote.
#
# Essen = 5
# Begründung:
# Sehr bekannte und vielfältige lokale Küche.
#
# Natur = 5
# Begründung:
# Nationalparks, Inseln, Berge und tropische Landschaften.
#
# Nightlife = 5
# Begründung:
# Stark ausgeprägtes Nachtleben in mehreren Destinationen.
#
#
# Die Werte sind keine objektiv gemessenen wissenschaftlichen
# Kennzahlen.
#
# In einer weiterentwickelten Version könnten sie aus externen
# Datenquellen wie Tourismusstatistiken, UNESCO-Daten,
# Restaurantdaten, Nationalparkdaten oder Nutzerbewertungen
# automatisiert abgeleitet werden.
# ============================================================


# ============================================================
# 6. REISEZIELE
# ============================================================

# Alle 50 Länder werden in einer Python-Liste gespeichert.
reiseziele = [

    # --------------------------------------------------------
    # EUROPA
    # --------------------------------------------------------

    {
        "land": "Portugal",
        "flagge": "🇵🇹",
        "region": "Europa",
        "ort": "Lissabon",
        "lat": 38.72,
        "lon": -9.14,
        "kosten": 90,
        "strand": 5,
        "kultur": 4,
        "essen": 5,
        "natur": 4,
        "nightlife": 4
    },

    {
        "land": "Spanien",
        "flagge": "🇪🇸",
        "region": "Europa",
        "ort": "Barcelona",
        "lat": 41.39,
        "lon": 2.17,
        "kosten": 100,
        "strand": 5,
        "kultur": 5,
        "essen": 5,
        "natur": 4,
        "nightlife": 5
    },

    {
        "land": "Italien",
        "flagge": "🇮🇹",
        "region": "Europa",
        "ort": "Rom",
        "lat": 41.90,
        "lon": 12.50,
        "kosten": 110,
        "strand": 4,
        "kultur": 5,
        "essen": 5,
        "natur": 4,
        "nightlife": 4
    },

    {
        "land": "Griechenland",
        "flagge": "🇬🇷",
        "region": "Europa",
        "ort": "Athen",
        "lat": 37.98,
        "lon": 23.73,
        "kosten": 95,
        "strand": 5,
        "kultur": 5,
        "essen": 4,
        "natur": 4,
        "nightlife": 4
    },

    {
        "land": "Kroatien",
        "flagge": "🇭🇷",
        "region": "Europa",
        "ort": "Split",
        "lat": 43.51,
        "lon": 16.44,
        "kosten": 90,
        "strand": 5,
        "kultur": 4,
        "essen": 4,
        "natur": 5,
        "nightlife": 3
    },

    {
        "land": "Frankreich",
        "flagge": "🇫🇷",
        "region": "Europa",
        "ort": "Nizza",
        "lat": 43.70,
        "lon": 7.27,
        "kosten": 125,
        "strand": 4,
        "kultur": 5,
        "essen": 5,
        "natur": 4,
        "nightlife": 4
    },

    {
        "land": "Niederlande",
        "flagge": "🇳🇱",
        "region": "Europa",
        "ort": "Amsterdam",
        "lat": 52.37,
        "lon": 4.90,
        "kosten": 120,
        "strand": 2,
        "kultur": 5,
        "essen": 4,
        "natur": 3,
        "nightlife": 4
    },

    {
        "land": "Belgien",
        "flagge": "🇧🇪",
        "region": "Europa",
        "ort": "Brüssel",
        "lat": 50.85,
        "lon": 4.35,
        "kosten": 115,
        "strand": 2,
        "kultur": 5,
        "essen": 5,
        "natur": 3,
        "nightlife": 4
    },

    {
        "land": "Deutschland",
        "flagge": "🇩🇪",
        "region": "Europa",
        "ort": "Berlin",
        "lat": 52.52,
        "lon": 13.41,
        "kosten": 110,
        "strand": 2,
        "kultur": 5,
        "essen": 4,
        "natur": 4,
        "nightlife": 5
    },

    {
        "land": "Österreich",
        "flagge": "🇦🇹",
        "region": "Europa",
        "ort": "Wien",
        "lat": 48.21,
        "lon": 16.37,
        "kosten": 115,
        "strand": 1,
        "kultur": 5,
        "essen": 4,
        "natur": 5,
        "nightlife": 3
    },

    {
        "land": "Schweiz",
        "flagge": "🇨🇭",
        "region": "Europa",
        "ort": "Zürich",
        "lat": 47.38,
        "lon": 8.54,
        "kosten": 180,
        "strand": 1,
        "kultur": 4,
        "essen": 4,
        "natur": 5,
        "nightlife": 3
    },

    {
        "land": "Island",
        "flagge": "🇮🇸",
        "region": "Europa",
        "ort": "Reykjavík",
        "lat": 64.15,
        "lon": -21.94,
        "kosten": 180,
        "strand": 1,
        "kultur": 3,
        "essen": 3,
        "natur": 5,
        "nightlife": 2
    },

    {
        "land": "Norwegen",
        "flagge": "🇳🇴",
        "region": "Europa",
        "ort": "Oslo",
        "lat": 59.91,
        "lon": 10.75,
        "kosten": 165,
        "strand": 1,
        "kultur": 3,
        "essen": 4,
        "natur": 5,
        "nightlife": 2
    },

    {
        "land": "Schweden",
        "flagge": "🇸🇪",
        "region": "Europa",
        "ort": "Stockholm",
        "lat": 59.33,
        "lon": 18.07,
        "kosten": 135,
        "strand": 2,
        "kultur": 4,
        "essen": 4,
        "natur": 5,
        "nightlife": 3
    },

    {
        "land": "Dänemark",
        "flagge": "🇩🇰",
        "region": "Europa",
        "ort": "Kopenhagen",
        "lat": 55.68,
        "lon": 12.57,
        "kosten": 145,
        "strand": 2,
        "kultur": 4,
        "essen": 5,
        "natur": 4,
        "nightlife": 3
    },

    {
        "land": "Irland",
        "flagge": "🇮🇪",
        "region": "Europa",
        "ort": "Dublin",
        "lat": 53.35,
        "lon": -6.26,
        "kosten": 120,
        "strand": 2,
        "kultur": 5,
        "essen": 4,
        "natur": 5,
        "nightlife": 4
    },

    {
        "land": "Grossbritannien",
        "flagge": "🇬🇧",
        "region": "Europa",
        "ort": "London",
        "lat": 51.51,
        "lon": -0.13,
        "kosten": 130,
        "strand": 2,
        "kultur": 5,
        "essen": 5,
        "natur": 4,
        "nightlife": 5
    },

    {
        "land": "Tschechien",
        "flagge": "🇨🇿",
        "region": "Europa",
        "ort": "Prag",
        "lat": 50.08,
        "lon": 14.44,
        "kosten": 75,
        "strand": 1,
        "kultur": 5,
        "essen": 4,
        "natur": 4,
        "nightlife": 4
    },

    {
        "land": "Polen",
        "flagge": "🇵🇱",
        "region": "Europa",
        "ort": "Krakau",
        "lat": 50.06,
        "lon": 19.94,
        "kosten": 65,
        "strand": 2,
        "kultur": 5,
        "essen": 4,
        "natur": 4,
        "nightlife": 4
    },

    {
        "land": "Ungarn",
        "flagge": "🇭🇺",
        "region": "Europa",
        "ort": "Budapest",
        "lat": 47.50,
        "lon": 19.04,
        "kosten": 65,
        "strand": 1,
        "kultur": 5,
        "essen": 5,
        "natur": 3,
        "nightlife": 5
    },

    {
        "land": "Slowenien",
        "flagge": "🇸🇮",
        "region": "Europa",
        "ort": "Ljubljana",
        "lat": 46.06,
        "lon": 14.51,
        "kosten": 85,
        "strand": 2,
        "kultur": 4,
        "essen": 4,
        "natur": 5,
        "nightlife": 2
    },

    {
        "land": "Albanien",
        "flagge": "🇦🇱",
        "region": "Europa",
        "ort": "Saranda",
        "lat": 39.88,
        "lon": 20.01,
        "kosten": 60,
        "strand": 5,
        "kultur": 4,
        "essen": 4,
        "natur": 5,
        "nightlife": 3
    },

    {
        "land": "Montenegro",
        "flagge": "🇲🇪",
        "region": "Europa",
        "ort": "Budva",
        "lat": 42.29,
        "lon": 18.84,
        "kosten": 70,
        "strand": 5,
        "kultur": 4,
        "essen": 4,
        "natur": 5,
        "nightlife": 3
    },

    {
        "land": "Malta",
        "flagge": "🇲🇹",
        "region": "Europa",
        "ort": "Valletta",
        "lat": 35.90,
        "lon": 14.51,
        "kosten": 95,
        "strand": 5,
        "kultur": 4,
        "essen": 4,
        "natur": 3,
        "nightlife": 4
    },

    {
        "land": "Zypern",
        "flagge": "🇨🇾",
        "region": "Europa",
        "ort": "Larnaka",
        "lat": 34.92,
        "lon": 33.62,
        "kosten": 95,
        "strand": 5,
        "kultur": 4,
        "essen": 4,
        "natur": 4,
        "nightlife": 4
    },


    # --------------------------------------------------------
    # AUSSERHALB EUROPAS
    # --------------------------------------------------------

    {
        "land": "Thailand",
        "flagge": "🇹🇭",
        "region": "Ausserhalb Europas",
        "ort": "Bangkok",
        "lat": 13.76,
        "lon": 100.50,
        "kosten": 55,
        "strand": 5,
        "kultur": 5,
        "essen": 5,
        "natur": 5,
        "nightlife": 5
    },

    {
        "land": "Vietnam",
        "flagge": "🇻🇳",
        "region": "Ausserhalb Europas",
        "ort": "Da Nang",
        "lat": 16.05,
        "lon": 108.20,
        "kosten": 50,
        "strand": 5,
        "kultur": 5,
        "essen": 5,
        "natur": 5,
        "nightlife": 4
    },

    {
        "land": "Indonesien",
        "flagge": "🇮🇩",
        "region": "Ausserhalb Europas",
        "ort": "Bali",
        "lat": -8.65,
        "lon": 115.22,
        "kosten": 55,
        "strand": 5,
        "kultur": 4,
        "essen": 5,
        "natur": 5,
        "nightlife": 4
    },

    {
        "land": "Japan",
        "flagge": "🇯🇵",
        "region": "Ausserhalb Europas",
        "ort": "Tokio",
        "lat": 35.68,
        "lon": 139.69,
        "kosten": 120,
        "strand": 3,
        "kultur": 5,
        "essen": 5,
        "natur": 5,
        "nightlife": 4
    },

    {
        "land": "Südkorea",
        "flagge": "🇰🇷",
        "region": "Ausserhalb Europas",
        "ort": "Seoul",
        "lat": 37.57,
        "lon": 126.98,
        "kosten": 100,
        "strand": 3,
        "kultur": 5,
        "essen": 5,
        "natur": 4,
        "nightlife": 5
    },

    {
        "land": "Philippinen",
        "flagge": "🇵🇭",
        "region": "Ausserhalb Europas",
        "ort": "Cebu",
        "lat": 10.32,
        "lon": 123.89,
        "kosten": 60,
        "strand": 5,
        "kultur": 4,
        "essen": 4,
        "natur": 5,
        "nightlife": 4
    },

    {
        "land": "Sri Lanka",
        "flagge": "🇱🇰",
        "region": "Ausserhalb Europas",
        "ort": "Colombo",
        "lat": 6.93,
        "lon": 79.85,
        "kosten": 50,
        "strand": 5,
        "kultur": 5,
        "essen": 5,
        "natur": 5,
        "nightlife": 3
    },

    {
        "land": "Malaysia",
        "flagge": "🇲🇾",
        "region": "Ausserhalb Europas",
        "ort": "Kuala Lumpur",
        "lat": 3.14,
        "lon": 101.69,
        "kosten": 60,
        "strand": 5,
        "kultur": 4,
        "essen": 5,
        "natur": 5,
        "nightlife": 4
    },

    {
        "land": "Singapur",
        "flagge": "🇸🇬",
        "region": "Ausserhalb Europas",
        "ort": "Singapur",
        "lat": 1.35,
        "lon": 103.82,
        "kosten": 140,
        "strand": 2,
        "kultur": 5,
        "essen": 5,
        "natur": 2,
        "nightlife": 5
    },

    {
        "land": "Indien",
        "flagge": "🇮🇳",
        "region": "Ausserhalb Europas",
        "ort": "Neu-Delhi",
        "lat": 28.61,
        "lon": 77.21,
        "kosten": 45,
        "strand": 3,
        "kultur": 5,
        "essen": 5,
        "natur": 5,
        "nightlife": 4
    },

    {
        "land": "Nepal",
        "flagge": "🇳🇵",
        "region": "Ausserhalb Europas",
        "ort": "Kathmandu",
        "lat": 27.72,
        "lon": 85.32,
        "kosten": 40,
        "strand": 1,
        "kultur": 5,
        "essen": 4,
        "natur": 5,
        "nightlife": 2
    },

    {
        "land": "Marokko",
        "flagge": "🇲🇦",
        "region": "Ausserhalb Europas",
        "ort": "Marrakesch",
        "lat": 31.63,
        "lon": -8.00,
        "kosten": 60,
        "strand": 3,
        "kultur": 5,
        "essen": 5,
        "natur": 4,
        "nightlife": 3
    },

    {
        "land": "Ägypten",
        "flagge": "🇪🇬",
        "region": "Ausserhalb Europas",
        "ort": "Hurghada",
        "lat": 27.26,
        "lon": 33.81,
        "kosten": 55,
        "strand": 5,
        "kultur": 5,
        "essen": 4,
        "natur": 4,
        "nightlife": 3
    },

    {
        "land": "Südafrika",
        "flagge": "🇿🇦",
        "region": "Ausserhalb Europas",
        "ort": "Kapstadt",
        "lat": -33.93,
        "lon": 18.42,
        "kosten": 80,
        "strand": 4,
        "kultur": 4,
        "essen": 5,
        "natur": 5,
        "nightlife": 4
    },

    {
        "land": "Tansania",
        "flagge": "🇹🇿",
        "region": "Ausserhalb Europas",
        "ort": "Sansibar",
        "lat": -6.17,
        "lon": 39.20,
        "kosten": 70,
        "strand": 5,
        "kultur": 4,
        "essen": 4,
        "natur": 5,
        "nightlife": 2
    },

    {
        "land": "Kenia",
        "flagge": "🇰🇪",
        "region": "Ausserhalb Europas",
        "ort": "Mombasa",
        "lat": -4.05,
        "lon": 39.67,
        "kosten": 70,
        "strand": 4,
        "kultur": 4,
        "essen": 4,
        "natur": 5,
        "nightlife": 3
    },

    {
        "land": "Mexiko",
        "flagge": "🇲🇽",
        "region": "Ausserhalb Europas",
        "ort": "Cancún",
        "lat": 21.16,
        "lon": -86.85,
        "kosten": 75,
        "strand": 5,
        "kultur": 5,
        "essen": 5,
        "natur": 4,
        "nightlife": 5
    },

    {
        "land": "Costa Rica",
        "flagge": "🇨🇷",
        "region": "Ausserhalb Europas",
        "ort": "San José",
        "lat": 9.93,
        "lon": -84.08,
        "kosten": 90,
        "strand": 5,
        "kultur": 3,
        "essen": 4,
        "natur": 5,
        "nightlife": 3
    },

    {
        "land": "Kolumbien",
        "flagge": "🇨🇴",
        "region": "Ausserhalb Europas",
        "ort": "Cartagena",
        "lat": 10.39,
        "lon": -75.48,
        "kosten": 55,
        "strand": 4,
        "kultur": 5,
        "essen": 5,
        "natur": 5,
        "nightlife": 5
    },

    {
        "land": "Brasilien",
        "flagge": "🇧🇷",
        "region": "Ausserhalb Europas",
        "ort": "Rio de Janeiro",
        "lat": -22.91,
        "lon": -43.17,
        "kosten": 75,
        "strand": 5,
        "kultur": 5,
        "essen": 5,
        "natur": 5,
        "nightlife": 5
    },

    {
        "land": "Peru",
        "flagge": "🇵🇪",
        "region": "Ausserhalb Europas",
        "ort": "Lima",
        "lat": -12.05,
        "lon": -77.04,
        "kosten": 55,
        "strand": 2,
        "kultur": 5,
        "essen": 5,
        "natur": 5,
        "nightlife": 3
    },

    {
        "land": "Argentinien",
        "flagge": "🇦🇷",
        "region": "Ausserhalb Europas",
        "ort": "Buenos Aires",
        "lat": -34.60,
        "lon": -58.38,
        "kosten": 75,
        "strand": 4,
        "kultur": 5,
        "essen": 5,
        "natur": 5,
        "nightlife": 5
    },

    {
        "land": "USA",
        "flagge": "🇺🇸",
        "region": "Ausserhalb Europas",
        "ort": "Los Angeles",
        "lat": 34.05,
        "lon": -118.24,
        "kosten": 150,
        "strand": 4,
        "kultur": 5,
        "essen": 5,
        "natur": 5,
        "nightlife": 5
    },

    {
        "land": "Kanada",
        "flagge": "🇨🇦",
        "region": "Ausserhalb Europas",
        "ort": "Vancouver",
        "lat": 49.28,
        "lon": -123.12,
        "kosten": 140,
        "strand": 2,
        "kultur": 4,
        "essen": 4,
        "natur": 5,
        "nightlife": 3
    },

    {
        "land": "Australien",
        "flagge": "🇦🇺",
        "region": "Ausserhalb Europas",
        "ort": "Sydney",
        "lat": -33.87,
        "lon": 151.21,
        "kosten": 130,
        "strand": 5,
        "kultur": 4,
        "essen": 5,
        "natur": 5,
        "nightlife": 5
    }
]


# ============================================================
# 7. MONATE
# ============================================================

# Monatsnamen werden in Monatsnummern übersetzt.
monate = {
    "Januar": 1,
    "Februar": 2,
    "März": 3,
    "April": 4,
    "Mai": 5,
    "Juni": 6,
    "Juli": 7,
    "August": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Dezember": 12
}


# ============================================================
# 8. HISTORISCHE TEMPERATUR LADEN
# ============================================================

# Ergebnisse werden für 24 Stunden zwischengespeichert.
@st.cache_data(ttl=86400)

# Funktion zum Laden der historischen Temperatur.
def lade_temperaturen(orte, monat_nummer):

    # Breitengrade aller Orte verbinden.
    latitudes = ",".join(
        str(ort["lat"]) for ort in orte
    )

    # Längengrade aller Orte verbinden.
    longitudes = ",".join(
        str(ort["lon"]) for ort in orte
    )

    # Parameter für Open-Meteo festlegen.
    parameter = {
        "latitude": latitudes,
        "longitude": longitudes,

        # Betrachtet werden fünf vollständige Jahre.
        "start_date": "2021-01-01",
        "end_date": "2025-12-31",

        # Benötigt wird die tägliche Durchschnittstemperatur.
        "daily": "temperature_2m_mean",

        # Lokale Zeitzone.
        "timezone": "auto"
    }

    # Basisadresse der API.
    basis_url = "https://archive-api.open-meteo.com/v1/archive?"

    # Parameter an URL anhängen.
    url = basis_url + urlencode(parameter)

    # API aufrufen.
    with urlopen(url, timeout=30) as antwort:

        # JSON-Antwort in Python umwandeln.
        daten = json.loads(
            antwort.read().decode("utf-8")
        )

    # Einzelnes Dictionary gegebenenfalls in Liste umwandeln.
    if isinstance(daten, dict):
        daten = [daten]

    # Hier werden die berechneten Temperaturen gespeichert.
    temperaturen = {}

    # Jedes Land und seine Wetterdaten gemeinsam durchlaufen.
    for ort, wetter in zip(orte, daten):

        # Liste aller Datumswerte.
        tage = wetter["daily"]["time"]

        # Liste aller Temperaturen.
        werte = wetter["daily"]["temperature_2m_mean"]

        # Hier werden nur Werte des ausgewählten Monats gesammelt.
        passende_werte = []

        # Datum und Temperatur gleichzeitig durchlaufen.
        for datum, temperatur in zip(tage, werte):

            # Fehlende Werte überspringen.
            if temperatur is None:
                continue

            # Monat aus Datum extrahieren.
            datum_monat = int(
                datum.split("-")[1]
            )

            # Nur Werte des gewählten Monats behalten.
            if datum_monat == monat_nummer:

                passende_werte.append(
                    temperatur
                )

        # Nur berechnen, wenn Daten vorhanden sind.
        if passende_werte:

            # Durchschnitt bilden.
            durchschnitt = (
                sum(passende_werte)
                / len(passende_werte)
            )

            # Ergebnis auf eine Nachkommastelle runden.
            temperaturen[ort["land"]] = round(
                durchschnitt,
                1
            )

    # Resultat zurückgeben.
    return temperaturen


# ============================================================
# 9. REISEDATEN
# ============================================================

# Überschrift des ersten Formularbereichs.
st.header("1. Deine Reise")

# Drei Spalten erzeugen.
col1, col2, col3 = st.columns(3)


# ------------------------------------------------------------
# MONAT UND DAUER
# ------------------------------------------------------------

with col1:

    # Reisemonat auswählen.
    monat_name = st.selectbox(
        "📅 Reisemonat",
        list(monate.keys())
    )

    # Reisedauer auswählen.
    tage = st.slider(
        "🗓️ Reisedauer",
        min_value=3,
        max_value=30,
        value=10
    )

    # Ausgewählten Wert erklären.
    st.caption(
        f"{tage} Tage"
    )


# ------------------------------------------------------------
# BUDGET
# ------------------------------------------------------------

with col2:

    # Budget auswählen.
    max_budget = st.slider(
        "💰 Budget pro Person",
        min_value=300,
        max_value=5000,
        value=1500,
        step=100
    )

    # Budgetbetrag darstellen.
    st.caption(
        f"CHF {max_budget}"
    )

    # Der Nutzer entscheidet, ob das Budget ein Muss-Kriterium ist.
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

    # Wunschtemperatur auswählen.
    wunschtemperatur = st.slider(
        "🌡️ Wunschtemperatur",
        min_value=-5,
        max_value=35,
        value=25
    )

    # Wert darstellen.
    st.caption(
        f"Ungefähr {wunschtemperatur} °C"
    )


# ============================================================
# 10. TEMPERATUR ALS OPTIONALER HARTER FILTER
# ============================================================

# Der Nutzer kann entscheiden, ob die Temperatur nur eine
# Präferenz oder eine zwingende Voraussetzung ist.
temperatur_muss = st.checkbox(
    "🌡️ Die Temperatur muss ungefähr meiner Wunschtemperatur entsprechen"
)

# Falls Temperatur zwingend ist, kann die Toleranz festgelegt werden.
if temperatur_muss:

    # Maximale erlaubte Abweichung einstellen.
    temperatur_toleranz = st.slider(
        "Erlaubte Temperaturabweichung",
        min_value=1,
        max_value=10,
        value=4
    )

else:

    # Standardwert für spätere Berechnung.
    temperatur_toleranz = 4


# ============================================================
# 11. INTERESSEN
# ============================================================

# Neuer Abschnitt.
st.header("2. Was ist dir im Urlaub wichtig?")

# Erklärung.
st.caption(
    "Bewerte jedes Thema von 1 = unwichtig bis 5 = sehr wichtig."
)

# Fünf Spalten erstellen.
i1, i2, i3, i4, i5 = st.columns(5)


# ------------------------------------------------------------
# STRAND
# ------------------------------------------------------------

with i1:

    # Wichtigkeit von Strand.
    strand = st.slider(
        "🏖️ Strand",
        min_value=1,
        max_value=5,
        value=3
    )

    # Zusätzlich kann Strand zwingend sein.
    strand_muss = st.checkbox(
        "Strand muss vorhanden sein"
    )


# ------------------------------------------------------------
# KULTUR
# ------------------------------------------------------------

with i2:

    # Wichtigkeit von Kultur.
    kultur = st.slider(
        "🏛️ Kultur",
        min_value=1,
        max_value=5,
        value=3
    )


# ------------------------------------------------------------
# ESSEN
# ------------------------------------------------------------

with i3:

    # Wichtigkeit von Essen.
    essen = st.slider(
        "🍜 Essen",
        min_value=1,
        max_value=5,
        value=3
    )


# ------------------------------------------------------------
# NATUR
# ------------------------------------------------------------

with i4:

    # Wichtigkeit von Natur.
    natur = st.slider(
        "🌿 Natur",
        min_value=1,
        max_value=5,
        value=3
    )


# ------------------------------------------------------------
# NIGHTLIFE
# ------------------------------------------------------------

with i5:

    # Wichtigkeit von Nightlife.
    nightlife = st.slider(
        "🎉 Nightlife",
        min_value=1,
        max_value=5,
        value=2
    )


# Etwas Abstand vor dem Button.
st.write("")


# ============================================================
# 12. EMPFEHLUNG STARTEN
# ============================================================

# Erst nach Klick wird der Algorithmus ausgeführt.
if st.button(
    "✈️ Meine Reiseziele finden",
    type="primary"
):


    # ========================================================
    # 12.1 DATEN KOPIEREN
    # ========================================================

    # Leere Liste für Kandidaten.
    kandidaten = []

    # Alle Länder durchlaufen.
    for ziel in reiseziele:

        # Dictionary kopieren,
        # damit die Originaldaten unverändert bleiben.
        kandidaten.append(
            ziel.copy()
        )


    # ========================================================
    # 12.2 REGION FILTERN
    # ========================================================

    # Falls eine konkrete Region gewählt wurde.
    if region != "Egal":

        # Nur Länder dieser Region behalten.
        kandidaten = [
            ziel
            for ziel in kandidaten
            if ziel["region"] == region
        ]


    # ========================================================
    # 12.3 GESAMTKOSTEN BERECHNEN
    # ========================================================

    # Alle Länder durchlaufen.
    for ziel in kandidaten:

        # Tageskosten mit Anzahl Tage multiplizieren.
        ziel["gesamtkosten"] = (
            ziel["kosten"] * tage
        )


    # ========================================================
    # 12.4 BUDGET ALS OPTIONALER HARTER FILTER
    # ========================================================
    #
    # Wenn budget_muss = True:
    #
    # Länder über dem Budget werden vollständig ausgeschlossen.
    #
    # Wenn budget_muss = False:
    #
    # Länder dürfen auch etwas darüber liegen.
    # Die Budgetabweichung wird später nur als Soft-Faktor
    # in der Similarity-Berechnung berücksichtigt.
    # ========================================================

    # Nur filtern, wenn Budget zwingend ist.
    if budget_muss:

        # Nur Länder innerhalb des Budgets behalten.
        kandidaten = [
            ziel
            for ziel in kandidaten
            if ziel["gesamtkosten"] <= max_budget
        ]


    # ========================================================
    # 12.5 STRAND ALS OPTIONALER HARTER FILTER
    # ========================================================
    #
    # Der Strand-Slider bleibt trotzdem bestehen.
    #
    # Beispiel:
    #
    # Slider = 5:
    # Strand ist dem Nutzer sehr wichtig.
    #
    # Checkbox zusätzlich aktiviert:
    # Länder ohne gute Strandeignung werden ausgeschlossen.
    # ========================================================

    # Nur filtern, falls Strand zwingend ist.
    if strand_muss:

        # Strand 4 oder 5 gilt als vorhandene gute Stranddestination.
        kandidaten = [
            ziel
            for ziel in kandidaten
            if ziel["strand"] >= 4
        ]


    # ========================================================
    # 12.6 PRÜFEN, OB NOCH LÄNDER VORHANDEN SIND
    # ========================================================

    # Falls bereits keine Destination mehr übrig ist.
    if len(kandidaten) == 0:

        # Fehler anzeigen.
        st.error(
            "Keine Destination erfüllt deine zwingenden Kriterien. "
            "Versuche beispielsweise das Budget zu erhöhen."
        )

        # Weitere Ausführung stoppen.
        st.stop()


    # ========================================================
    # 12.7 TEMPERATURDATEN LADEN
    # ========================================================

    # Monatsnamen in Monatsnummer übersetzen.
    monat_nummer = monate[
        monat_name
    ]

    # Spinner während API-Abfrage.
    with st.spinner(
        "🌡️ Klimadaten werden geladen..."
    ):

        # API-Fehler abfangen.
        try:

            # Temperaturdaten abrufen.
            temperaturdaten = lade_temperaturen(
                kandidaten,
                monat_nummer
            )

        # Falls API-Aufruf fehlschlägt.
        except Exception:

            # Fehlermeldung anzeigen.
            st.error(
                "Die Wetterdaten konnten gerade nicht geladen werden. "
                "Bitte versuche es erneut."
            )

            # Algorithmus stoppen.
            st.stop()


    # ========================================================
    # 12.8 TEMPERATUREN DEN LÄNDERN ZUORDNEN
    # ========================================================

    # Neue Kandidatenliste.
    kandidaten_mit_temperatur = []

    # Alle Länder durchlaufen.
    for ziel in kandidaten:

        # Nur Länder verwenden, für die Wetterdaten vorhanden sind.
        if ziel["land"] in temperaturdaten:

            # Temperatur speichern.
            ziel["temperatur"] = temperaturdaten[
                ziel["land"]
            ]

            # Land übernehmen.
            kandidaten_mit_temperatur.append(
                ziel
            )

    # Kandidaten ersetzen.
    kandidaten = kandidaten_mit_temperatur


    # ========================================================
    # 12.9 TEMPERATUR OPTIONAL ALS HARD CONSTRAINT
    # ========================================================

    # Falls Temperatur zwingend ist.
    if temperatur_muss:

        # Länder ausserhalb der gewählten Toleranz entfernen.
        kandidaten = [
            ziel
            for ziel in kandidaten
            if abs(
                ziel["temperatur"]
                - wunschtemperatur
            ) <= temperatur_toleranz
        ]


    # Falls danach nichts mehr vorhanden ist.
    if len(kandidaten) == 0:

        # Hinweis anzeigen.
        st.error(
            "Keine Destination erfüllt deine Kombination aus "
            "Budget, Strand und Temperatur."
        )

        # Algorithmus stoppen.
        st.stop()


    # ========================================================
    # 13. SIMILARITY-BERECHNUNG
    # ========================================================
    #
    # Jetzt werden die verbliebenen Länder mathematisch
    # mit dem Nutzerprofil verglichen.
    #
    #
    # Faktoren:
    #
    # - Budget
    # - Temperatur
    # - Strand
    # - Kultur
    # - Essen
    # - Natur
    # - Nightlife
    #
    #
    # NORMALISIERUNG
    # --------------------------------------------------------
    #
    # Aktivitätsratings liegen zwischen 1 und 5.
    #
    # Maximale Differenz:
    #
    # 5 - 1 = 4
    #
    # Deshalb teilen wir die Differenz durch 4.
    #
    #
    # Temperatur:
    #
    # Differenz wird durch 20 geteilt.
    #
    # 20 °C dienen im Prototyp als Referenzspanne.
    #
    #
    # Budget:
    #
    # Differenz zwischen geschätzten Reisekosten und
    # Nutzerbudget wird durch das Nutzerbudget geteilt.
    #
    # Beispiel:
    #
    # Budget = 2000 CHF
    #
    # Reisekosten = 2200 CHF
    #
    # Differenz = 200 CHF
    #
    # Normalisierte Differenz:
    #
    # 200 / 2000 = 0.10
    #
    #
    # HARD CONSTRAINTS
    # --------------------------------------------------------
    #
    # Wenn Budget als zwingend markiert ist, wurden zu teure
    # Länder bereits ausgeschlossen.
    #
    # Trotzdem bleibt Budget zusätzlich Teil der Ähnlichkeit,
    # damit beispielsweise eine Destination mit 1400 CHF
    # besser zu einem Budget von 1500 CHF passt als eine
    # Destination mit nur 400 CHF.
    #
    #
    # EUKLIDISCHE DISTANZ
    # --------------------------------------------------------
    #
    # Die normalisierten Abweichungen werden quadriert,
    # addiert und daraus wird die Quadratwurzel gezogen.
    #
    # Je kleiner die resultierende Distanz,
    # desto ähnlicher ist das Land dem Nutzerprofil.
    # ========================================================

    # Leere Ergebnisliste.
    ergebnisse = []

    # Alle Kandidaten durchlaufen.
    for ziel in kandidaten:


        # ----------------------------------------------------
        # BUDGET-DISTANZ
        # ----------------------------------------------------

        # Absolute Differenz zwischen Budget und Reisekosten.
        budget_unterschied = abs(
            ziel["gesamtkosten"]
            - max_budget
        )

        # Differenz durch Nutzerbudget teilen.
        budget_distanz = (
            budget_unterschied
            / max_budget
        )


        # ----------------------------------------------------
        # TEMPERATUR-DISTANZ
        # ----------------------------------------------------

        # Abweichung von Wunschtemperatur normalisieren.
        temperatur_distanz = (
            abs(
                ziel["temperatur"]
                - wunschtemperatur
            )
            / 20
        )


        # ----------------------------------------------------
        # STRAND-DISTANZ
        # ----------------------------------------------------

        # Strandabweichung normalisieren.
        strand_distanz = (
            abs(
                ziel["strand"]
                - strand
            )
            / 4
        )


        # ----------------------------------------------------
        # KULTUR-DISTANZ
        # ----------------------------------------------------

        # Kulturabweichung normalisieren.
        kultur_distanz = (
            abs(
                ziel["kultur"]
                - kultur
            )
            / 4
        )


        # ----------------------------------------------------
        # ESSEN-DISTANZ
        # ----------------------------------------------------

        # Essensabweichung normalisieren.
        essen_distanz = (
            abs(
                ziel["essen"]
                - essen
            )
            / 4
        )


        # ----------------------------------------------------
        # NATUR-DISTANZ
        # ----------------------------------------------------

        # Naturabweichung normalisieren.
        natur_distanz = (
            abs(
                ziel["natur"]
                - natur
            )
            / 4
        )


        # ----------------------------------------------------
        # NIGHTLIFE-DISTANZ
        # ----------------------------------------------------

        # Nightlifeabweichung normalisieren.
        nightlife_distanz = (
            abs(
                ziel["nightlife"]
                - nightlife
            )
            / 4
        )


        # ----------------------------------------------------
        # EUKLIDISCHE GESAMTDISTANZ
        # ----------------------------------------------------

        # Alle Faktoren zusammenführen.
        distanz = math.sqrt(

            budget_distanz ** 2

            + temperatur_distanz ** 2

            + strand_distanz ** 2

            + kultur_distanz ** 2

            + essen_distanz ** 2

            + natur_distanz ** 2

            + nightlife_distanz ** 2
        )


        # Distanz im Dictionary speichern.
        ziel["distanz"] = distanz

        # Ergebnis speichern.
        ergebnisse.append(
            ziel
        )


    # ========================================================
    # 14. ERGEBNISSE SORTIEREN
    # ========================================================

    # Kleinste Distanz zuerst.
    ergebnisse = sorted(
        ergebnisse,
        key=lambda ziel: ziel["distanz"]
    )

    # Nur die fünf besten Matches.
    ergebnisse = ergebnisse[:5]


    # ========================================================
    # 15. RESULTATE ANZEIGEN
    # ========================================================

    # Trennlinie.
    st.divider()

    # Überschrift.
    st.header("✨ Deine besten Matches")


    # Alle fünf Resultate durchlaufen.
    for position, ziel in enumerate(
        ergebnisse,
        start=1
    ):


        # ----------------------------------------------------
        # MATCH SCORE
        # --------------------------------------------------------
        #
        # Die mathematische Distanz ist für Nutzer schwer
        # interpretierbar.
        #
        # Deshalb wird daraus ein Wert von 0 bis 100 erzeugt.
        #
        # Formel:
        #
        # 100 - Distanz × 30
        #
        # Der Faktor 30 ist nur ein Darstellungsfaktor.
        #
        # Er wurde nicht durch Machine Learning gelernt.
        #
        # Der Match Score ist deshalb keine statistische
        # Wahrscheinlichkeit.
        # ----------------------------------------------------

        # Score berechnen.
        match_score = round(
            max(
                0,
                min(
                    100,
                    100 - ziel["distanz"] * 30
                )
            )
        )


        # ----------------------------------------------------
        # RESULTAT ALS STREAMLIT-CONTAINER
        # ----------------------------------------------------
        #
        # Hier verwenden wir bewusst KEIN eigenes HTML mehr.
        #
        # Dadurch kann Streamlit keine HTML-Tags als Code
        # darstellen.
        # ----------------------------------------------------

        # Container mit Rahmen erzeugen.
        with st.container(border=True):

            # Flagge und Ländername gross darstellen.
            st.subheader(
                f"{position}. {ziel['flagge']} {ziel['land']}"
            )

            # Referenzort anzeigen.
            st.caption(
                f"Klimareferenz: {ziel['ort']}"
            )

            # Match Score darstellen.
            st.write(
                f"**{match_score}% Match**"
            )

            # Fortschrittsbalken.
            st.progress(
                match_score / 100
            )


            # ------------------------------------------------
            # KENNZAHLEN
            # ------------------------------------------------

            # Vier Spalten erstellen.
            r1, r2, r3, r4 = st.columns(4)


            with r1:

                # Temperatur anzeigen.
                st.metric(
                    f"🌡️ Ø {monat_name}",
                    f"{ziel['temperatur']} °C"
                )


            with r2:

                # Gesamtkosten anzeigen.
                st.metric(
                    "💰 Kosten vor Ort",
                    f"CHF {ziel['gesamtkosten']}"
                )


            with r3:

                # Tageskosten anzeigen.
                st.metric(
                    "💵 Pro Tag",
                    f"CHF {ziel['kosten']}"
                )


            with r4:

                # Differenz zum Budget berechnen.
                budget_differenz = (
                    max_budget
                    - ziel["gesamtkosten"]
                )

                # Positives Budget als Restbudget darstellen.
                if budget_differenz >= 0:

                    st.metric(
                        "💳 Restbudget",
                        f"CHF {budget_differenz}"
                    )

                # Falls Budget nicht zwingend war,
                # kann die Destination darüber liegen.
                else:

                    st.metric(
                        "💳 Über Budget",
                        f"CHF {abs(budget_differenz)}"
                    )


            # ------------------------------------------------
            # AKTIVITÄTEN
            # ------------------------------------------------

            # Kleine Überschrift.
            st.markdown("**Was dich dort erwartet:**")

            # Fünf Aktivitäts-Spalten.
            a1, a2, a3, a4, a5 = st.columns(5)


            with a1:

                # Strandrating.
                st.write(
                    f"🏖️ **Strand**\n\n{ziel['strand']}/5"
                )


            with a2:

                # Kulturrating.
                st.write(
                    f"🏛️ **Kultur**\n\n{ziel['kultur']}/5"
                )


            with a3:

                # Essensrating.
                st.write(
                    f"🍜 **Essen**\n\n{ziel['essen']}/5"
                )


            with a4:

                # Naturrating.
                st.write(
                    f"🌿 **Natur**\n\n{ziel['natur']}/5"
                )


            with a5:

                # Nightliferating.
                st.write(
                    f"🎉 **Nightlife**\n\n{ziel['nightlife']}/5"
                )


            # ------------------------------------------------
            # BUDGET-HINWEIS
            # ------------------------------------------------

            # Wenn Land innerhalb des Budgets liegt.
            if ziel["gesamtkosten"] <= max_budget:

                # Positive Meldung.
                st.success(
                    "✓ Liegt innerhalb deines angegebenen Budgets."
                )

            # Falls Budget nicht als zwingend gewählt wurde
            # und das Land teurer ist.
            else:

                # Warnung anzeigen.
                st.warning(
                    "Dieses Reiseziel liegt etwas über deinem "
                    "angegebenen Budget."
                )
