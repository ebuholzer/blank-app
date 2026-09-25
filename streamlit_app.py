# ============================================================
# TRAVELMATCH
# Reiseziel-Empfehlung mit Similarity-/Nearest-Neighbor-Prinzip
# ============================================================

# ------------------------------------------------------------
# 1. BIBLIOTHEKEN IMPORTIEREN
# ------------------------------------------------------------

# Streamlit wird benötigt, um die Web-App zu erstellen.
import streamlit as st

# math wird für mathematische Berechnungen benötigt.
import math

# json wird verwendet, um Wetterdaten aus der API zu lesen.
import json

# urlopen ermöglicht HTTP-Anfragen an eine externe API.
from urllib.request import urlopen

# urlencode wandelt Parameter in eine gültige URL um.
from urllib.parse import urlencode


# ============================================================
# 2. STREAMLIT-SEITE KONFIGURIEREN
# ============================================================

# Grundeinstellungen der Web-App definieren.
st.set_page_config(

    # Titel im Browser-Tab.
    page_title="TravelMatch",

    # Browser-Icon.
    page_icon="🌍",

    # Breites Layout verwenden.
    layout="wide"
)


# ============================================================
# 3. EIGENES DESIGN MIT CSS
# ============================================================
#
# Streamlit ist funktional, aber standardmässig relativ schlicht.
# Mit CSS können wir Farben, Abstände, Karten und Buttons
# visuell verbessern.
# ============================================================

st.markdown(
    """
    <style>

    /* Gesamter Inhaltsbereich */
    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* Hero-Bereich oben */
    .hero {
        padding: 2.2rem 2.4rem;
        border-radius: 24px;
        background: linear-gradient(
            135deg,
            #f7f9fc 0%,
            #eef3f8 100%
        );
        border: 1px solid #e5e9ef;
        margin-bottom: 2rem;
    }

    /* Kleine obere Hero-Zeile */
    .hero-label {
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6b7280;
        margin-bottom: 0.5rem;
    }

    /* Haupttitel im Hero */
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.05;
        margin-bottom: 0.7rem;
        color: #111827;
    }

    /* Untertitel im Hero */
    .hero-subtitle {
        font-size: 1.1rem;
        color: #4b5563;
        max-width: 700px;
        line-height: 1.6;
    }

    /* Karte für Resultate */
    .result-card {
        border: 1px solid #e5e7eb;
        border-radius: 22px;
        padding: 1.4rem 1.5rem;
        margin-bottom: 1.3rem;
        background: white;
    }

    /* Land + Flagge */
    .result-title {
        font-size: 1.6rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        color: #111827;
    }

    /* Repräsentativer Ort */
    .result-subtitle {
        color: #6b7280;
        margin-bottom: 1rem;
    }

    /* Match Badge */
    .match-badge {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        background: #eef2ff;
        color: #3730a3;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 0.8rem;
    }

    /* Tags für Aktivitäten */
    .tag {
        display: inline-block;
        padding: 0.3rem 0.55rem;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
        border-radius: 999px;
        background: #f3f4f6;
        color: #374151;
        font-size: 0.88rem;
        font-weight: 600;
    }

    /* Grüner Budgethinweis */
    .budget-ok {
        margin-top: 0.8rem;
        padding: 0.75rem 0.9rem;
        border-radius: 12px;
        background: #ecfdf5;
        color: #065f46;
        font-weight: 600;
    }

    /* Abschnittstitel etwas kompakter */
    h2, h3 {
        margin-top: 1.2rem !important;
    }

    /* Primärbutton grösser */
    div.stButton > button {
        width: 100%;
        border-radius: 14px;
        min-height: 3rem;
        font-size: 1rem;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 4. HERO-BEREICH
# ============================================================

# HTML-Block für einen moderneren Header.
st.markdown(
    """
    <div class="hero">
        <div class="hero-label">Smart travel recommendation</div>
        <div class="hero-title">🌍 TravelMatch</div>
        <div class="hero-subtitle">
            Finde Reiseziele, die zu deinem Budget, deinem Reisemonat,
            deiner gewünschten Temperatur und deinen Interessen passen.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 5. DATENGRUNDLAGE
# ============================================================
#
# Jedes Reiseziel wird als Dictionary gespeichert.
#
# Datenfelder:
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
# Repräsentative touristische Destination.
#
# lat / lon:
# Koordinaten dieses Ortes für die Wetter-API.
#
# kosten:
# Vereinfachte Tageskosten in CHF.
#
# strand, kultur, essen, natur, nightlife:
# Heuristische Bewertungen von 1 bis 5.
#
#
# HERLEITUNG DER RATINGS
# ------------------------------------------------------------
#
# 1 = sehr geringe Eignung
# 2 = eher geringe Eignung
# 3 = durchschnittliche Eignung
# 4 = gute Eignung
# 5 = sehr hohe Eignung
#
# Diese Bewertungen sind für den Prototyp manuell gesetzte
# Heuristiken.
#
# Beispiel Thailand:
#
# Strand = 5
# -> sehr viele bekannte Stranddestinationen
#
# Kultur = 5
# -> Tempel, historische Orte, kulturelle Angebote
#
# Essen = 5
# -> international bekannte und vielfältige Küche
#
# Natur = 5
# -> Nationalparks, Inseln, Berge, tropische Landschaften
#
# Nightlife = 5
# -> starkes Nachtleben in touristischen Zentren
#
#
# Die Werte sind keine objektiv gemessenen Kennzahlen.
# In einer wissenschaftlich erweiterten Version könnten
# sie später aus externen Datenquellen abgeleitet werden.
# ============================================================


# ============================================================
# 6. REISEZIELE
# ============================================================

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
# 7. MONATE DEFINIEREN
# ============================================================

# Deutsche Monatsnamen mit Monatsnummern verknüpfen.
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
# 8. HISTORISCHE TEMPERATURDATEN LADEN
# ============================================================

# Temperaturdaten werden 24 Stunden im Cache gespeichert.
@st.cache_data(ttl=86400)

# Funktion zum Laden historischer Temperaturen.
def lade_temperaturen(orte, monat_nummer):

    # Alle Breitengrade sammeln.
    latitudes = ",".join(
        str(ort["lat"]) for ort in orte
    )

    # Alle Längengrade sammeln.
    longitudes = ",".join(
        str(ort["lon"]) for ort in orte
    )

    # Parameter für die API definieren.
    parameter = {

        # Breitengrade.
        "latitude": latitudes,

        # Längengrade.
        "longitude": longitudes,

        # Historischer Startzeitpunkt.
        "start_date": "2021-01-01",

        # Historischer Endzeitpunkt.
        "end_date": "2025-12-31",

        # Tägliche Durchschnittstemperatur anfordern.
        "daily": "temperature_2m_mean",

        # Lokale Zeitzone verwenden.
        "timezone": "auto"
    }

    # Basis-URL der Open-Meteo Historical Weather API.
    basis_url = "https://archive-api.open-meteo.com/v1/archive?"

    # Vollständige URL erzeugen.
    url = basis_url + urlencode(parameter)

    # API abfragen.
    with urlopen(url, timeout=30) as antwort:

        # Antwort lesen und JSON in Python-Daten umwandeln.
        daten = json.loads(
            antwort.read().decode("utf-8")
        )

    # Falls nur ein einzelner Ort zurückgegeben wird,
    # machen wir daraus eine Liste.
    if isinstance(daten, dict):
        daten = [daten]

    # Leeres Dictionary für Temperaturergebnisse.
    temperaturen = {}

    # Orte und Wetterdaten gemeinsam durchlaufen.
    for ort, wetter in zip(orte, daten):

        # Alle Datumswerte laden.
        tage = wetter["daily"]["time"]

        # Alle Temperaturwerte laden.
        werte = wetter["daily"]["temperature_2m_mean"]

        # Hier sammeln wir nur Temperaturen des gewünschten Monats.
        passende_werte = []

        # Datum und Temperatur parallel durchlaufen.
        for datum, temperatur in zip(tage, werte):

            # Fehlende Werte überspringen.
            if temperatur is None:
                continue

            # Monat aus dem Datum extrahieren.
            datum_monat = int(
                datum.split("-")[1]
            )

            # Prüfen, ob dieser Tag zum gewünschten Monat gehört.
            if datum_monat == monat_nummer:

                # Temperatur speichern.
                passende_werte.append(
                    temperatur
                )

        # Nur fortfahren, wenn Werte vorhanden sind.
        if passende_werte:

            # Durchschnitt berechnen.
            durchschnitt = (
                sum(passende_werte)
                / len(passende_werte)
            )

            # Durchschnitt auf eine Dezimalstelle runden.
            temperaturen[ort["land"]] = round(
                durchschnitt,
                1
            )

    # Temperaturen an den Hauptcode zurückgeben.
    return temperaturen


# ============================================================
# 9. NUTZEREINGABEN
# ============================================================

# Abschnittstitel anzeigen.
st.subheader("1. Reisedaten")

# Drei Spalten für bessere Übersicht.
col1, col2, col3 = st.columns(3)


# ------------------------------------------------------------
# ERSTE SPALTE
# ------------------------------------------------------------

with col1:

    # Monat auswählen.
    monat_name = st.selectbox(
        "Reisemonat",
        list(monate.keys())
    )

    # Reisedauer auswählen.
    tage = st.slider(
        "Reisedauer in Tagen",
        min_value=3,
        max_value=30,
        value=10
    )


# ------------------------------------------------------------
# ZWEITE SPALTE
# ------------------------------------------------------------

with col2:

    # Maximales Budget auswählen.
    max_budget = st.slider(
        "Maximalbudget vor Ort",
        min_value=300,
        max_value=5000,
        value=1500,
        step=100
    )

    # Zusatzinfo anzeigen.
    st.caption(
        f"Maximal CHF {max_budget} pro Person"
    )


# ------------------------------------------------------------
# DRITTE SPALTE
# ------------------------------------------------------------

with col3:

    # Region auswählen.
    region = st.selectbox(
        "Region",
        [
            "Egal",
            "Europa",
            "Ausserhalb Europas"
        ]
    )

    # Wunschtemperatur auswählen.
    wunschtemperatur = st.slider(
        "Wunschtemperatur",
        min_value=-5,
        max_value=35,
        value=25
    )

    # Temperaturwert zusätzlich darstellen.
    st.caption(
        f"Ungefähr {wunschtemperatur} °C"
    )


# ============================================================
# 10. STRAND ALS JA/NEIN-KRITERIUM
# ============================================================

# Neuer Abschnitt.
st.subheader("2. Muss dein Reiseziel Strand haben?")

# Auswahl statt 1-5-Slider.
strand_ist_pflicht = st.radio(
    "Strand",
    [
        "Egal",
        "Ja, Strand muss vorhanden sein"
    ],
    horizontal=True
)


# ============================================================
# 11. INTERESSEN
# ============================================================

# Abschnittstitel.
st.subheader("3. Was ist dir im Urlaub wichtig?")

# Kurze Erklärung.
st.caption(
    "1 = wenig wichtig · 5 = sehr wichtig"
)

# Vier Spalten für Interessen.
i1, i2, i3, i4 = st.columns(4)


with i1:

    # Kulturpräferenz.
    kultur = st.slider(
        "🏛️ Kultur",
        1,
        5,
        3
    )


with i2:

    # Essenpräferenz.
    essen = st.slider(
        "🍜 Essen",
        1,
        5,
        3
    )


with i3:

    # Naturpräferenz.
    natur = st.slider(
        "🌿 Natur",
        1,
        5,
        3
    )


with i4:

    # Nightlifepräferenz.
    nightlife = st.slider(
        "🎉 Nightlife",
        1,
        5,
        2
    )


# ============================================================
# 12. EMPFEHLUNG STARTEN
# ============================================================

# Button erzeugen.
if st.button(
    "✈️ Passende Reiseziele finden",
    type="primary"
):

    # --------------------------------------------------------
    # 12.1 ALLE REISEZIELE KOPIEREN
    # --------------------------------------------------------

    # Leere Kandidatenliste erstellen.
    kandidaten = []

    # Alle Länder durchlaufen.
    for ziel in reiseziele:

        # Dictionary kopieren.
        kandidaten.append(
            ziel.copy()
        )


    # --------------------------------------------------------
    # 12.2 REGION ALS HARTES KRITERIUM
    # --------------------------------------------------------

    # Nur filtern, wenn Nutzer nicht "Egal" gewählt hat.
    if region != "Egal":

        # Nur Länder der gewählten Region behalten.
        kandidaten = [
            ziel
            for ziel in kandidaten
            if ziel["region"] == region
        ]


    # --------------------------------------------------------
    # 12.3 BUDGET ALS HARTES KRITERIUM
    # --------------------------------------------------------
    #
    # Das Budget ist ein echtes Maximum.
    # Reiseziele über dem Budget werden ausgeschlossen.
    # --------------------------------------------------------

    # Leere Liste für bezahlbare Länder.
    budget_kandidaten = []

    # Kandidaten durchlaufen.
    for ziel in kandidaten:

        # Gesamtkosten vor Ort berechnen.
        gesamtkosten = (
            ziel["kosten"] * tage
        )

        # Gesamtkosten im Dictionary speichern.
        ziel["gesamtkosten"] = gesamtkosten

        # Nur Länder innerhalb des Maximalbudgets übernehmen.
        if gesamtkosten <= max_budget:

            budget_kandidaten.append(
                ziel
            )

    # Kandidaten aktualisieren.
    kandidaten = budget_kandidaten


    # --------------------------------------------------------
    # 12.4 STRAND ALS JA/NEIN-FILTER
    # --------------------------------------------------------
    #
    # Wenn Strand zwingend ist, werden nur Länder
    # mit Strandbewertung 4 oder 5 berücksichtigt.
    # --------------------------------------------------------

    if strand_ist_pflicht == "Ja, Strand muss vorhanden sein":

        # Nur Länder mit guter bis sehr guter Strandeignung.
        kandidaten = [
            ziel
            for ziel in kandidaten
            if ziel["strand"] >= 4
        ]


    # --------------------------------------------------------
    # 12.5 PRÜFEN, OB NOCH KANDIDATEN VORHANDEN SIND
    # --------------------------------------------------------

    # Falls kein Land übrig bleibt.
    if len(kandidaten) == 0:

        # Verständliche Meldung anzeigen.
        st.error(
            "Kein Reiseziel erfüllt aktuell deine harten Kriterien. "
            "Erhöhe zum Beispiel dein Budget oder ändere die Region."
        )

        # Ausführung stoppen.
        st.stop()


    # --------------------------------------------------------
    # 12.6 TEMPERATURDATEN LADEN
    # --------------------------------------------------------

    # Monatsname in Monatsnummer umwandeln.
    monat_nummer = monate[
        monat_name
    ]

    # Spinner anzeigen, während API geladen wird.
    with st.spinner(
        "🌡️ Klimadaten werden geladen..."
    ):

        # Fehler sicher abfangen.
        try:

            # Temperaturdaten laden.
            temperaturdaten = lade_temperaturen(
                kandidaten,
                monat_nummer
            )

        # Falls die Wetter-API nicht funktioniert.
        except Exception:

            # Fehlermeldung anzeigen.
            st.error(
                "Die historischen Wetterdaten konnten gerade "
                "nicht geladen werden. Bitte versuche es erneut."
            )

            # Ausführung stoppen.
            st.stop()


    # --------------------------------------------------------
    # 12.7 TEMPERATUREN DEN LÄNDERN ZUORDNEN
    # --------------------------------------------------------

    # Neue Liste erstellen.
    kandidaten_mit_temperatur = []

    # Alle Kandidaten durchlaufen.
    for ziel in kandidaten:

        # Prüfen, ob Wetterdaten vorhanden sind.
        if ziel["land"] in temperaturdaten:

            # Temperatur zum Land hinzufügen.
            ziel["temperatur"] = temperaturdaten[
                ziel["land"]
            ]

            # Land übernehmen.
            kandidaten_mit_temperatur.append(
                ziel
            )

    # Kandidaten aktualisieren.
    kandidaten = kandidaten_mit_temperatur


    # --------------------------------------------------------
    # 12.8 PRÜFEN, OB WETTERDATEN VORHANDEN SIND
    # --------------------------------------------------------

    if len(kandidaten) == 0:

        # Fehlermeldung anzeigen.
        st.error(
            "Für die verbleibenden Reiseziele konnten "
            "keine Wetterdaten geladen werden."
        )

        # Ausführung stoppen.
        st.stop()


    # ========================================================
    # 13. SIMILARITY-BERECHNUNG
    # ========================================================
    #
    # Die harten Kriterien wurden bereits angewendet:
    #
    # - Region
    # - Budget
    # - optional Strand
    #
    # Jetzt werden die verbleibenden Länder anhand ihrer
    # Ähnlichkeit zum Nutzerprofil sortiert.
    #
    #
    # VERWENDETE SOFT-FAKTOREN:
    #
    # - Wunschtemperatur
    # - Kultur
    # - Essen
    # - Natur
    # - Nightlife
    #
    #
    # NORMALISIERUNG
    # --------------------------------------------------------
    #
    # Aktivitäten liegen auf einer Skala von 1 bis 5.
    #
    # Maximale Differenz:
    #
    # 5 - 1 = 4
    #
    # Deshalb wird jede Differenz durch 4 geteilt.
    #
    #
    # Beispiel:
    #
    # Nutzer:
    # Kultur = 5
    #
    # Land:
    # Kultur = 3
    #
    # Differenz:
    # 2
    #
    # Normalisiert:
    # 2 / 4 = 0.5
    #
    #
    # TEMPERATUR
    # --------------------------------------------------------
    #
    # Temperatur wird durch 20 geteilt.
    #
    # Beispiel:
    #
    # Wunschtemperatur = 28 °C
    # Land = 24 °C
    #
    # Differenz = 4 °C
    #
    # Normalisiert:
    #
    # 4 / 20 = 0.20
    #
    #
    # Der Wert 20 dient als Referenzspanne für eine
    # deutlich wahrnehmbare Temperaturabweichung.
    #
    #
    # GEWICHTUNG
    # --------------------------------------------------------
    #
    # Alle fünf Faktoren werden gleich gewichtet.
    #
    # Es gibt bewusst keine versteckte Gewichtung.
    #
    #
    # EUKLIDISCHE DISTANZ
    # --------------------------------------------------------
    #
    # Distanz =
    #
    # sqrt(
    #     Temperatur²
    #     + Kultur²
    #     + Essen²
    #     + Natur²
    #     + Nightlife²
    # )
    #
    # Je kleiner die Distanz,
    # desto besser passt das Reiseziel.
    # ========================================================

    # Leere Ergebnisliste erstellen.
    ergebnisse = []

    # Alle Kandidaten durchlaufen.
    for ziel in kandidaten:

        # Temperaturabweichung berechnen.
        temperatur_distanz = (
            abs(
                ziel["temperatur"]
                - wunschtemperatur
            )
            / 20
        )

        # Kulturabweichung berechnen.
        kultur_distanz = (
            abs(
                ziel["kultur"]
                - kultur
            )
            / 4
        )

        # Essensabweichung berechnen.
        essen_distanz = (
            abs(
                ziel["essen"]
                - essen
            )
            / 4
        )

        # Naturabweichung berechnen.
        natur_distanz = (
            abs(
                ziel["natur"]
                - natur
            )
            / 4
        )

        # Nightlifeabweichung berechnen.
        nightlife_distanz = (
            abs(
                ziel["nightlife"]
                - nightlife
            )
            / 4
        )

        # Euklidische Gesamtdistanz berechnen.
        distanz = math.sqrt(

            temperatur_distanz ** 2

            + kultur_distanz ** 2

            + essen_distanz ** 2

            + natur_distanz ** 2

            + nightlife_distanz ** 2
        )

        # Distanz im Dictionary speichern.
        ziel["distanz"] = distanz

        # Land zur Ergebnisliste hinzufügen.
        ergebnisse.append(
            ziel
        )


    # ========================================================
    # 14. ERGEBNISSE SORTIEREN
    # ========================================================

    # Länder nach Distanz sortieren.
    ergebnisse = sorted(
        ergebnisse,
        key=lambda ziel: ziel["distanz"]
    )

    # Nur fünf beste Resultate verwenden.
    ergebnisse = ergebnisse[:5]


    # ========================================================
    # 15. RESULTATE ANZEIGEN
    # ========================================================

    # Abstand erzeugen.
    st.markdown("## ✨ Deine besten Matches")

    # Ergebnisse durchlaufen.
    for position, ziel in enumerate(
        ergebnisse,
        start=1
    ):

        # ----------------------------------------------------
        # MATCH SCORE BERECHNEN
        # --------------------------------------------------------
        #
        # Der Match Score dient nur als verständliche
        # Darstellung der mathematischen Distanz.
        #
        # Formel:
        #
        # 100 - Distanz × 30
        #
        # Der Faktor 30 ist ein Darstellungsfaktor.
        # Er wurde nicht statistisch trainiert.
        # ----------------------------------------------------

        # Score berechnen.
        match_score = round(
            max(
                0,
                100 - ziel["distanz"] * 30
            )
        )

        # Restbudget berechnen.
        restbudget = (
            max_budget
            - ziel["gesamtkosten"]
        )

        # ----------------------------------------------------
        # RESULTAT-KARTE START
        # ----------------------------------------------------

        st.markdown(
            f"""
            <div class="result-card">

                <div class="result-title">
                    {position}. {ziel['flagge']} {ziel['land']}
                </div>

                <div class="result-subtitle">
                    Klimareferenz: {ziel['ort']}
                </div>

                <div class="match-badge">
                    {match_score}% Match
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        # Fortschrittsbalken für Match Score.
        st.progress(
            match_score / 100
        )

        # Vier Kennzahlen nebeneinander.
        r1, r2, r3, r4 = st.columns(4)


        with r1:

            # Temperatur darstellen.
            st.metric(
                f"🌡️ Ø {monat_name}",
                f"{ziel['temperatur']} °C"
            )


        with r2:

            # Gesamtkosten darstellen.
            st.metric(
                "💰 Kosten vor Ort",
                f"CHF {ziel['gesamtkosten']}"
            )


        with r3:

            # Tageskosten darstellen.
            st.metric(
                "💵 Pro Tag",
                f"CHF {ziel['kosten']}"
            )


        with r4:

            # Restbudget darstellen.
            st.metric(
                "💳 Restbudget",
                f"CHF {restbudget}"
            )


        # Aktivitäts-Tags erzeugen.
        st.markdown(
            f"""
            <div style="margin-top: 0.8rem;">

                <span class="tag">
                    🏖 Strand {ziel['strand']}/5
                </span>

                <span class="tag">
                    🏛 Kultur {ziel['kultur']}/5
                </span>

                <span class="tag">
                    🍜 Essen {ziel['essen']}/5
                </span>

                <span class="tag">
                    🌿 Natur {ziel['natur']}/5
                </span>

                <span class="tag">
                    🎉 Nightlife {ziel['nightlife']}/5
                </span>

            </div>
            """,
            unsafe_allow_html=True
        )

        # Budgetbestätigung anzeigen.
        st.markdown(
            """
            <div class="budget-ok">
                ✓ Innerhalb deines maximalen Budgets
            </div>
            """,
            unsafe_allow_html=True
        )

        # Abstand zwischen den Resultaten.
        st.markdown("<br>", unsafe_allow_html=True)
        
