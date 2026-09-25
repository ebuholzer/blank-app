# ============================================================
# TRAVELMATCH
# Reiseziel-Empfehlung mit Similarity / Nearest-Neighbor-Prinzip
# ============================================================

# Streamlit wird importiert, damit wir eine Web-App erstellen können.
import streamlit as st

# math wird importiert, weil wir später Quadratwurzel-Berechnungen benötigen.
import math

# json wird benötigt, um Wetterdaten aus der API zu lesen.
import json

# urlopen ermöglicht HTTP-Anfragen an die Wetter-API.
from urllib.request import urlopen

# urlencode wandelt unsere API-Parameter in eine gültige URL um.
from urllib.parse import urlencode


# ============================================================
# 1. STREAMLIT-SEITE KONFIGURIEREN
# ============================================================

# Hier definieren wir grundlegende Einstellungen der Webseite.
st.set_page_config(
    # Titel, der im Browser-Tab angezeigt wird.
    page_title="TravelMatch",

    # Emoji, das als Icon im Browser angezeigt wird.
    page_icon="🌍",

    # "wide" nutzt mehr Platz auf grossen Bildschirmen.
    layout="wide"
)


# ============================================================
# 2. TITEL UND EINLEITUNG
# ============================================================

# Grosse Hauptüberschrift der App.
st.title("🌍 TravelMatch")

# Kurze Erklärung für den Nutzer.
st.write(
    """
    Finde Reiseziele, die zu deinem Budget, deinem Reisemonat,
    deiner gewünschten Temperatur und deinen Interessen passen.
    """
)


# ============================================================
# 3. DATENGRUNDLAGE
# ============================================================

# Jedes Land wird als Python-Dictionary gespeichert.
#
# Beispiel:
#
# {
#     "land": "Portugal",
#     "flagge": "🇵🇹",
#     "region": "Europa",
#     "ort": "Lissabon",
#     "lat": 38.72,
#     "lon": -9.14,
#     "kosten": 90,
#     "strand": 5,
#     "kultur": 4,
#     "essen": 5,
#     "natur": 4,
#     "nightlife": 4
# }
#
#
# BEDEUTUNG DER VARIABLEN
# ------------------------------------------------------------
#
# land:
# Deutscher Name des Landes.
#
# flagge:
# Emoji-Flagge des Landes.
#
# region:
# Europa oder ausserhalb Europas.
#
# ort:
# Eine repräsentative touristische Destination.
#
# Warum ein einzelner Ort?
# Ein Land kann verschiedene Klimazonen besitzen.
# Deshalb wäre z.B. "Temperatur von Australien" methodisch
# nicht sinnvoll. Stattdessen verwenden wir beispielsweise
# Sydney als repräsentative touristische Destination.
#
# lat / lon:
# Geografische Koordinaten des repräsentativen Ortes.
# Diese werden ausschliesslich für die Wetter-API benötigt.
#
# kosten:
# Vereinfachte geschätzte Tageskosten in CHF.
#
# Die Kosten beinhalten in diesem Prototyp:
# - Unterkunft
# - Essen
# - lokale Aktivitäten
#
# Nicht enthalten:
# - Flug
#
#
# AKTIVITÄTSFAKTOREN
# ------------------------------------------------------------
#
# strand
# kultur
# essen
# natur
# nightlife
#
# werden auf einer Skala von 1 bis 5 bewertet.
#
# 1 = sehr geringe Eignung
# 2 = eher geringe Eignung
# 3 = durchschnittliche Eignung
# 4 = gute Eignung
# 5 = sehr hohe Eignung
#
#
# WIE WURDEN DIESE WERTE FESTGELEGT?
# ------------------------------------------------------------
#
# Die Bewertungen sind im aktuellen Prototyp sogenannte
# heuristische Werte.
#
# Das bedeutet:
# Sie wurden anhand typischer touristischer Eigenschaften
# eines Landes bzw. der repräsentativen Destination festgelegt.
#
# Beispiel Thailand:
#
# Strand = 5
# Thailand besitzt sehr viele bekannte Stranddestinationen.
#
# Kultur = 5
# Viele Tempel, historische Orte und kulturelle Angebote.
#
# Essen = 5
# Stark ausgeprägte und international bekannte Küche.
#
# Natur = 5
# Inseln, Nationalparks, Berge und tropische Landschaften.
#
# Nightlife = 5
# Starkes Nachtleben in verschiedenen touristischen Zentren.
#
#
# METHODISCHE EINSCHRÄNKUNG
# ------------------------------------------------------------
#
# Diese Werte sind NICHT statistisch gemessen.
#
# Für eine wissenschaftlich weiterentwickelte Version könnten
# solche Faktoren beispielsweise aus folgenden Daten entstehen:
#
# - Anzahl touristisch relevanter Strände
# - Anzahl UNESCO-Welterbestätten
# - Restaurant- und Gastronomiedaten
# - Anzahl Nationalparks
# - touristische Bewertungen
# - Anzahl Nightlife-Angebote
#
# Für diesen Prototyp dienen die Faktoren dazu,
# den Recommendation-Algorithmus verständlich zu demonstrieren.


# ============================================================
# 4. REISEZIELE
# ============================================================

# Alle 50 Reiseziele werden in einer Liste gespeichert.
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
# 5. MONATE
# ============================================================

# Dictionary zur Übersetzung von Monatsnamen in Monatsnummern.
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
# 6. FUNKTION FÜR HISTORISCHE TEMPERATUREN
# ============================================================

# Streamlit speichert das Ergebnis dieser Funktion für 24 Stunden.
# Dadurch müssen die Wetterdaten nicht bei jedem Klick neu geladen werden.
@st.cache_data(ttl=86400)

# Funktion erhält eine Liste von Orten und eine Monatsnummer.
def lade_temperaturen(orte, monat_nummer):

    # Alle Breitengrade werden mit Kommas verbunden.
    latitudes = ",".join(
        str(ort["lat"]) for ort in orte
    )

    # Alle Längengrade werden mit Kommas verbunden.
    longitudes = ",".join(
        str(ort["lon"]) for ort in orte
    )

    # Hier definieren wir die Parameter für die Open-Meteo API.
    parameter = {

        # Breitengrade aller Orte.
        "latitude": latitudes,

        # Längengrade aller Orte.
        "longitude": longitudes,

        # Beginn unseres historischen Betrachtungszeitraums.
        "start_date": "2021-01-01",

        # Ende unseres historischen Betrachtungszeitraums.
        "end_date": "2025-12-31",

        # Wir benötigen die tägliche Durchschnittstemperatur.
        "daily": "temperature_2m_mean",

        # Open-Meteo wählt automatisch die lokale Zeitzone.
        "timezone": "auto"
    }

    # Basis-Adresse der Historical Weather API.
    basis_url = "https://archive-api.open-meteo.com/v1/archive?"

    # Parameter werden an die Basis-URL angehängt.
    url = basis_url + urlencode(parameter)

    # Die URL wird aufgerufen.
    with urlopen(url, timeout=30) as antwort:

        # Die Antwort wird gelesen und von JSON in Python-Daten umgewandelt.
        daten = json.loads(
            antwort.read().decode("utf-8")
        )

    # Falls nur ein einzelner Ort abgefragt wurde,
    # kann Open-Meteo statt einer Liste ein Dictionary liefern.
    if isinstance(daten, dict):

        # Deshalb wandeln wir es in eine Liste um.
        daten = [daten]

    # Leeres Dictionary für unsere später berechneten Temperaturen.
    temperaturen = {}

    # zip verbindet jeweils ein Reiseziel mit seinen Wetterdaten.
    for ort, wetter in zip(orte, daten):

        # Liste aller Datumswerte speichern.
        tage = wetter["daily"]["time"]

        # Liste aller täglichen Durchschnittstemperaturen speichern.
        werte = wetter["daily"]["temperature_2m_mean"]

        # Hier sammeln wir nur Werte des gewünschten Monats.
        passende_werte = []

        # Datum und Temperatur werden gleichzeitig durchlaufen.
        for datum, temperatur in zip(tage, werte):

            # Fehlende Messwerte werden übersprungen.
            if temperatur is None:
                continue

            # Beispiel eines Datums:
            # "2024-07-15"
            #
            # split("-") erzeugt:
            # ["2024", "07", "15"]
            #
            # Element 1 entspricht also dem Monat.
            datum_monat = int(
                datum.split("-")[1]
            )

            # Nur Daten des vom Nutzer gewählten Monats verwenden.
            if datum_monat == monat_nummer:

                # Temperatur zur Liste hinzufügen.
                passende_werte.append(
                    temperatur
                )

        # Prüfen, ob Temperaturwerte vorhanden sind.
        if passende_werte:

            # Durchschnitt aller passenden Tage berechnen.
            durchschnitt = (
                sum(passende_werte)
                / len(passende_werte)
            )

            # Ergebnis auf eine Nachkommastelle runden.
            temperaturen[ort["land"]] = round(
                durchschnitt,
                1
            )

    # Berechnete Temperaturen an die App zurückgeben.
    return temperaturen


# ============================================================
# 7. NUTZEREINGABEN
# ============================================================

# Erste Überschrift im Formular.
st.header("1. Deine Reise")

# Bildschirm in zwei Spalten aufteilen.
col1, col2 = st.columns(2)


# ------------------------------------------------------------
# LINKE SPALTE
# ------------------------------------------------------------

with col1:

    # Dropdown für den Reisemonat.
    monat_name = st.selectbox(
        "Wann möchtest du reisen?",
        list(monate.keys())
    )

    # Slider für Anzahl Reisetage.
    tage = st.slider(
        "Wie viele Tage möchtest du reisen?",
        min_value=3,
        max_value=30,
        value=10
    )

    # Slider für das maximale Budget.
    max_budget = st.slider(
        "Maximalbudget vor Ort pro Person in CHF",
        min_value=300,
        max_value=5000,
        value=1500,
        step=100
    )

    # Erklärung des Budgetbegriffs.
    st.caption(
        "Budget beinhaltet Unterkunft, Essen und Aktivitäten. "
        "Flugkosten sind im aktuellen Prototyp nicht enthalten."
    )


# ------------------------------------------------------------
# RECHTE SPALTE
# ------------------------------------------------------------

with col2:

    # Nutzer kann Region auswählen.
    region = st.selectbox(
        "Welche Region kommt infrage?",
        [
            "Egal",
            "Europa",
            "Ausserhalb Europas"
        ]
    )

    # Slider für gewünschte Durchschnittstemperatur.
    wunschtemperatur = st.slider(
        "Welche Durchschnittstemperatur möchtest du?",
        min_value=-5,
        max_value=35,
        value=25
    )

    # Gewählte Temperatur zusätzlich als Text darstellen.
    st.write(
        f"🌡️ Wunschtemperatur: **{wunschtemperatur} °C**"
    )

    # Checkbox macht die Temperatur optional zu einem Muss-Kriterium.
    temperatur_muss = st.checkbox(
        "Temperatur muss zwingend ungefähr passen"
    )

    # Nutzer legt fest, wie stark die Temperatur abweichen darf.
    temperatur_toleranz = st.slider(
        "Erlaubte Temperaturabweichung in °C",
        min_value=1,
        max_value=10,
        value=4
    )


# ============================================================
# 8. INTERESSEN
# ============================================================

# Neue Überschrift.
st.header("2. Was möchtest du erleben?")

# Erklärung des Ratings.
st.write(
    """
    1 bedeutet wenig wichtig und 5 bedeutet sehr wichtig.
    Zusätzlich kannst du einzelne Kriterien als zwingend markieren.
    """
)

# Bereich in drei Spalten aufteilen.
a1, a2, a3 = st.columns(3)


# ------------------------------------------------------------
# STRAND UND NATUR
# ------------------------------------------------------------

with a1:

    # Gewünschte Strand-Eignung.
    strand = st.slider(
        "🏖️ Strand",
        1,
        5,
        3
    )

    # Strand kann zum zwingenden Kriterium gemacht werden.
    strand_muss = st.checkbox(
        "🏖️ Strand MUSS vorhanden sein"
    )

    # Gewünschte Natur-Eignung.
    natur = st.slider(
        "🌿 Natur",
        1,
        5,
        3
    )

    # Natur kann zum zwingenden Kriterium gemacht werden.
    natur_muss = st.checkbox(
        "🌿 Natur MUSS stark vorhanden sein"
    )


# ------------------------------------------------------------
# KULTUR UND ESSEN
# ------------------------------------------------------------

with a2:

    # Gewünschte Kultur-Eignung.
    kultur = st.slider(
        "🏛️ Kultur",
        1,
        5,
        3
    )

    # Kultur kann zwingend sein.
    kultur_muss = st.checkbox(
        "🏛️ Kultur MUSS stark vorhanden sein"
    )

    # Gewünschte Food-Eignung.
    essen = st.slider(
        "🍜 Essen",
        1,
        5,
        3
    )

    # Essen kann zwingend sein.
    essen_muss = st.checkbox(
        "🍜 Essen MUSS stark sein"
    )


# ------------------------------------------------------------
# NIGHTLIFE
# ------------------------------------------------------------

with a3:

    # Gewünschte Nightlife-Eignung.
    nightlife = st.slider(
        "🎉 Nightlife",
        1,
        5,
        2
    )

    # Nightlife kann zwingend sein.
    nightlife_muss = st.checkbox(
        "🎉 Nightlife MUSS stark sein"
    )


# ============================================================
# 9. EMPFEHLUNGSALGORITHMUS STARTEN
# ============================================================

# Der folgende Code läuft erst, wenn der Nutzer den Button drückt.
if st.button(
    "✈️ Meine Reiseziele finden",
    type="primary"
):


    # ========================================================
    # 9.1 REGION FILTERN
    # ========================================================

    # Leere Liste für mögliche Reiseziele erstellen.
    kandidaten = []

    # Alle 50 Reiseziele einzeln durchlaufen.
    for ziel in reiseziele:

        # Falls Nutzer eine bestimmte Region gewählt hat...
        if region != "Egal":

            # ...und das Land nicht in dieser Region liegt...
            if ziel["region"] != region:

                # ...wird es übersprungen.
                continue

        # Dictionary kopieren, damit Originaldaten unverändert bleiben.
        kandidaten.append(
            ziel.copy()
        )


    # ========================================================
    # 9.2 MAXIMALBUDGET ALS HARD CONSTRAINT
    # ========================================================

    # Neue Liste für Länder innerhalb des Budgets.
    budget_kandidaten = []

    # Alle bisherigen Kandidaten durchlaufen.
    for ziel in kandidaten:

        # Gesamtkosten berechnen:
        # Tageskosten × Reisedauer.
        gesamtkosten = (
            ziel["kosten"] * tage
        )

        # Gesamtkosten im Dictionary speichern.
        ziel["gesamtkosten"] = gesamtkosten

        # Nur Länder behalten, die innerhalb des Maximalbudgets liegen.
        if gesamtkosten <= max_budget:

            # Land zur Liste hinzufügen.
            budget_kandidaten.append(
                ziel
            )

    # Kandidatenliste durch Budget-gefilterte Liste ersetzen.
    kandidaten = budget_kandidaten


    # ========================================================
    # 9.3 ZWINGENDE AKTIVITÄTEN
    # ========================================================

    # Neue Liste für Länder, die alle Muss-Kriterien erfüllen.
    harte_filter = []

    # Jedes Land prüfen.
    for ziel in kandidaten:

        # Falls Strand zwingend ist,
        # muss das Land mindestens 4 von 5 Punkten besitzen.
        if strand_muss and ziel["strand"] < 4:
            continue

        # Gleiches Prinzip für Natur.
        if natur_muss and ziel["natur"] < 4:
            continue

        # Gleiches Prinzip für Kultur.
        if kultur_muss and ziel["kultur"] < 4:
            continue

        # Gleiches Prinzip für Essen.
        if essen_muss and ziel["essen"] < 4:
            continue

        # Gleiches Prinzip für Nightlife.
        if nightlife_muss and ziel["nightlife"] < 4:
            continue

        # Nur wenn kein Filter das Land ausgeschlossen hat,
        # wird es übernommen.
        harte_filter.append(
            ziel
        )

    # Kandidatenliste aktualisieren.
    kandidaten = harte_filter


    # ========================================================
    # 9.4 PRÜFEN, OB NOCH LÄNDER VORHANDEN SIND
    # ========================================================

    # Falls keine Länder übrig bleiben...
    if len(kandidaten) == 0:

        # Fehlermeldung anzeigen.
        st.error(
            """
            Kein Reiseziel erfüllt deine zwingenden Kriterien
            innerhalb des angegebenen Budgets.

            Erhöhe das Budget oder entferne ein Muss-Kriterium.
            """
        )

        # Weitere Ausführung stoppen.
        st.stop()


    # ========================================================
    # 9.5 HISTORISCHE TEMPERATUR LADEN
    # ========================================================

    # Deutschen Monatsnamen in Monatsnummer umwandeln.
    monat_nummer = monate[
        monat_name
    ]

    # Während die API arbeitet, Spinner anzeigen.
    with st.spinner(
        "🌡️ Historische Klimadaten werden geladen..."
    ):

        # try verhindert einen vollständigen Absturz bei API-Problemen.
        try:

            # Temperaturdaten über unsere Funktion laden.
            temperaturdaten = lade_temperaturen(
                kandidaten,
                monat_nummer
            )

        # Falls irgendein API-Fehler auftritt...
        except Exception:

            # verständliche Fehlermeldung anzeigen.
            st.error(
                """
                Die historischen Wetterdaten konnten gerade
                nicht geladen werden.

                Bitte versuche es erneut.
                """
            )

            # Ausführung stoppen.
            st.stop()


    # ========================================================
    # 9.6 TEMPERATURWERTE ZU LÄNDERN HINZUFÜGEN
    # ========================================================

    # Neue Liste erstellen.
    kandidaten_mit_temperatur = []

    # Kandidaten durchlaufen.
    for ziel in kandidaten:

        # Prüfen, ob für dieses Land Wetterdaten vorhanden sind.
        if ziel["land"] in temperaturdaten:

            # Temperaturwert in das Länder-Dictionary schreiben.
            ziel["temperatur"] = temperaturdaten[
                ziel["land"]
            ]

            # Land übernehmen.
            kandidaten_mit_temperatur.append(
                ziel
            )

    # Kandidaten aktualisieren.
    kandidaten = kandidaten_mit_temperatur


    # ========================================================
    # 9.7 TEMPERATUR ALS HARD CONSTRAINT
    # ========================================================

    # Nur wenn Nutzer Temperatur als zwingend aktiviert hat...
    if temperatur_muss:

        # ...werden Länder ausserhalb der Toleranz entfernt.
        kandidaten = [
            ziel
            for ziel in kandidaten
            if abs(
                ziel["temperatur"]
                - wunschtemperatur
            ) <= temperatur_toleranz
        ]


    # Prüfen, ob nach Temperaturfilter Länder vorhanden sind.
    if len(kandidaten) == 0:

        # Fehlermeldung anzeigen.
        st.error(
            """
            Kein Reiseziel erfüllt deine gewünschte Temperatur
            zusammen mit allen anderen Muss-Kriterien.

            Erhöhe beispielsweise die Temperatur-Toleranz.
            """
        )

        # Ausführung stoppen.
        st.stop()


    # ========================================================
    # 10. SIMILARITY / NEAREST-NEIGHBOR-LOGIK
    # ========================================================
    #
    # Jetzt wurden alle harten Ausschlusskriterien angewendet.
    #
    # Die verbleibenden Länder werden anhand ihrer Ähnlichkeit
    # zum Nutzerprofil sortiert.
    #
    #
    # NORMALISIERUNG
    # --------------------------------------------------------
    #
    # Problem:
    #
    # Temperatur kann beispielsweise zwischen 0 und 35 liegen.
    #
    # Aktivitäten liegen aber nur zwischen 1 und 5.
    #
    # Deshalb müssen die Abstände normalisiert werden.
    #
    #
    # TEMPERATUR
    # --------------------------------------------------------
    #
    # Formel:
    #
    # absolute Temperaturabweichung / 20
    #
    # Beispiel:
    #
    # Nutzer möchte 28 °C.
    # Land hat 24 °C.
    #
    # Differenz:
    #
    # |24 - 28| = 4
    #
    # Normalisierte Differenz:
    #
    # 4 / 20 = 0.20
    #
    # Die 20 °C dienen als Referenzspanne für eine
    # deutliche Temperaturabweichung.
    #
    #
    # AKTIVITÄTEN
    # --------------------------------------------------------
    #
    # Aktivitätsskala reicht von 1 bis 5.
    #
    # Maximale Differenz:
    #
    # 5 - 1 = 4
    #
    # Deshalb:
    #
    # Differenz / 4
    #
    #
    # Beispiel:
    #
    # Wunsch Strand = 5
    # Land Strand = 3
    #
    # Differenz = 2
    #
    # 2 / 4 = 0.5
    #
    #
    # GEWICHTUNG
    # --------------------------------------------------------
    #
    # Temperatur, Strand, Natur, Kultur, Essen und Nightlife
    # werden in dieser Version bewusst gleich gewichtet.
    #
    # Es gibt also KEINE versteckte Gewichtung wie:
    #
    # Strand × 3
    # Temperatur × 2
    #
    # Dadurch bleibt der Algorithmus nachvollziehbar.
    #
    #
    # EUKLIDISCHE DISTANZ
    # --------------------------------------------------------
    #
    # Die einzelnen Unterschiede werden folgendermassen
    # zusammengeführt:
    #
    # Distanz =
    #
    # sqrt(
    #     temperatur²
    #     + strand²
    #     + natur²
    #     + kultur²
    #     + essen²
    #     + nightlife²
    # )
    #
    # Kleine Distanz = hohe Ähnlichkeit.
    # Grosse Distanz = geringe Ähnlichkeit.
    # ========================================================


    # Leere Ergebnisliste erstellen.
    ergebnisse = []

    # Jedes verbleibende Land einzeln analysieren.
    for ziel in kandidaten:

        # Absolute Temperaturabweichung berechnen
        # und durch Referenzspanne 20 teilen.
        temperatur_distanz = (
            abs(
                ziel["temperatur"]
                - wunschtemperatur
            )
            / 20
        )

        # Abweichung der Strandpräferenz berechnen.
        strand_distanz = (
            abs(
                ziel["strand"]
                - strand
            )
            / 4
        )

        # Abweichung der Naturpräferenz berechnen.
        natur_distanz = (
            abs(
                ziel["natur"]
                - natur
            )
            / 4
        )

        # Abweichung der Kulturpräferenz berechnen.
        kultur_distanz = (
            abs(
                ziel["kultur"]
                - kultur
            )
            / 4
        )

        # Abweichung der Essenspräferenz berechnen.
        essen_distanz = (
            abs(
                ziel["essen"]
                - essen
            )
            / 4
        )

        # Abweichung der Nightlifepräferenz berechnen.
        nightlife_distanz = (
            abs(
                ziel["nightlife"]
                - nightlife
            )
            / 4
        )

        # ----------------------------------------------------
        # EUKLIDISCHE DISTANZ
        # ----------------------------------------------------

        # Alle normalisierten Unterschiede werden quadriert,
        # addiert und anschliessend wird die Quadratwurzel gezogen.
        distanz = math.sqrt(

            temperatur_distanz ** 2

            + strand_distanz ** 2

            + natur_distanz ** 2

            + kultur_distanz ** 2

            + essen_distanz ** 2

            + nightlife_distanz ** 2
        )

        # Berechnete Distanz im Länder-Dictionary speichern.
        ziel["distanz"] = distanz

        # Land zur Ergebnisliste hinzufügen.
        ergebnisse.append(
            ziel
        )


    # ========================================================
    # 11. ERGEBNISSE SORTIEREN
    # ========================================================

    # Länder nach Distanz aufsteigend sortieren.
    #
    # Kleinste Distanz steht damit zuerst.
    ergebnisse = sorted(
        ergebnisse,
        key=lambda ziel: ziel["distanz"]
    )

    # Nur die fünf ähnlichsten Reiseziele behalten.
    ergebnisse = ergebnisse[:5]


    # ========================================================
    # 12. ERGEBNISSE AUSGEBEN
    # ========================================================

    # Horizontale Trennlinie.
    st.divider()

    # Überschrift der Ergebnisse.
    st.header("🌎 Deine besten Reiseziele")


    # enumerate erzeugt zusätzlich eine Rangnummer.
    #
    # start=1 bedeutet:
    # erstes Ergebnis bekommt Nummer 1 statt Nummer 0.
    for position, ziel in enumerate(
        ergebnisse,
        start=1
    ):


        # ====================================================
        # MATCH SCORE
        # ====================================================
        #
        # Die mathematische Distanz ist für normale Nutzer
        # schwer verständlich.
        #
        # Deshalb wird daraus ein einfacher Score zwischen
        # 0 und 100 erstellt.
        #
        # Formel:
        #
        # 100 - Distanz × 30
        #
        # Beispiel:
        #
        # Distanz = 0.5
        #
        # 100 - 0.5 × 30
        #
        # = 85
        #
        # Der Faktor 30 wurde als Darstellungsfaktor gewählt,
        # damit typische Distanzwerte des Prototyps sinnvoll
        # auf einer Skala von 0 bis 100 dargestellt werden.
        #
        # WICHTIG:
        #
        # Dieser Score ist KEINE statistische Wahrscheinlichkeit.
        # Der Faktor 30 wurde NICHT durch Training gelernt.
        # ====================================================

        # Distanz in verständlichen Score umwandeln.
        match_score = round(
            max(
                0,
                100 - ziel["distanz"] * 30
            )
        )


        # ----------------------------------------------------
        # LAND UND FLAGGE
        # ----------------------------------------------------

        # Rang, Flagge und Ländername anzeigen.
        st.subheader(
            f"{position}. "
            f"{ziel['flagge']} "
            f"{ziel['land']}"
        )


        # Grafischen Fortschrittsbalken anzeigen.
        st.progress(
            match_score / 100
        )


        # Match Score als Zahl darstellen.
        st.write(
            f"**Match Score: {match_score}%**"
        )


        # Transparenz darüber schaffen,
        # für welchen Ort die Temperatur gilt.
        st.caption(
            f"Temperatur basiert auf historischen Wetterdaten "
            f"für {ziel['ort']}."
        )


        # ----------------------------------------------------
        # VIER KENNZAHLEN NEBENEINANDER
        # ----------------------------------------------------

        # Vier Streamlit-Spalten erstellen.
        c1, c2, c3, c4 = st.columns(4)


        # Erste Spalte.
        with c1:

            # Durchschnittstemperatur anzeigen.
            st.metric(
                f"🌡️ Ø {monat_name}",
                f"{ziel['temperatur']} °C"
            )


        # Zweite Spalte.
        with c2:

            # Gesamtkosten der Reise anzeigen.
            st.metric(
                "💰 Kosten vor Ort",
                f"CHF {ziel['gesamtkosten']}"
            )


        # Dritte Spalte.
        with c3:

            # Tageskosten anzeigen.
            st.metric(
                "💵 Pro Tag",
                f"CHF {ziel['kosten']}"
            )


        # Restbudget berechnen.
        restbudget = (
            max_budget
            - ziel["gesamtkosten"]
        )


        # Vierte Spalte.
        with c4:

            # Restbudget anzeigen.
            st.metric(
                "💳 Restbudget",
                f"CHF {restbudget}"
            )


        # ----------------------------------------------------
        # AKTIVITÄTEN
        # ----------------------------------------------------

        # Kleine Überschrift.
        st.write(
            "**Eignung für Aktivitäten:**"
        )


        # Ratings des Landes anzeigen.
        st.write(
            f"""
            🏖️ Strand: **{ziel['strand']}/5**  
            🌿 Natur: **{ziel['natur']}/5**  
            🏛️ Kultur: **{ziel['kultur']}/5**  
            🍜 Essen: **{ziel['essen']}/5**  
            🎉 Nightlife: **{ziel['nightlife']}/5**
            """
        )


        # Hinweis, dass das Budgetkriterium erfüllt wurde.
        st.success(
            "✅ Liegt innerhalb deines maximalen Budgets vor Ort."
        )


        # Trennlinie zwischen den Ländern.
        st.divider()


# ============================================================
# 13. METHODISCHER HINWEIS
# ============================================================

# Kleiner Hinweis am unteren Rand der App.
st.caption(
    """
    Methodik: TravelMatch kombiniert harte Filterbedingungen
    mit einem similarity-basierten Nearest-Neighbor-Ansatz.

    Zwingende Anforderungen wie Budget, Strand oder Temperatur
    werden zuerst als Ausschlusskriterien verwendet.

    Anschliessend werden die verbleibenden Destinationen anhand
    ihrer normalisierten euklidischen Distanz zum Nutzerprofil
    sortiert.

    Historische Temperaturen werden für eine repräsentative
    Destination des jeweiligen Landes berechnet.

    Aktivitätsratings und Tageskosten sind vereinfachte
    heuristische Werte des Prototyps.

    Der Match Score ist keine statistische Wahrscheinlichkeit.
    """
)
