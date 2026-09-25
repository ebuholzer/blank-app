# ============================================================
# TRAVELMATCH | Vollstaendige App | Recherche: 25.09.2026
# ============================================================
# WICHTIG FUER DIE ABGABE:
# 1. Budgetdaten: recherchierte Durchschnittsausgaben je Reisestil,
#    KEINE garantierten Mindestpreise oder maximal moeglichen Kosten.
# 2. Aktivitaetsratings: weiterhin unvalidierte DEMOWERTE des Prototyps.
#    Sie wurden NICHT aus Tourismusstatistiken oder Bewertungen berechnet.
# 3. Empfehlung: gewichteter Distanzvergleich mit einem Idealprofil.
#    Kein ueberwacht trainiertes Modell; keine gelernte Erfolgsprognose.
#    Ob das den geforderten ML-Anteil erfuellt, muss die Aufgabenstellung klaeren.
# 4. Monatswerte: historische Reanalyse fuer einen Referenzort, keine Vorhersage.
# 5. Geldwerte und Match-Punkte sind Planungs-/Vergleichshilfen, keine Zusagen.

import streamlit as st  # Erstellt Formulare, Tabellen und Ergebniskarten.
import math  # Berechnet die Quadratwurzel fuer den Distanzvergleich.
import json  # Liest die JSON-Antwort der Wetter-API.
import calendar  # Liefert die korrekte Anzahl Tage pro Monat, inklusive Schaltjahr.
from urllib.parse import urlencode  # Kodiert Parameter fuer die Wetter-URL.
from urllib.request import Request, urlopen  # Ruft Wetterdaten per HTTPS ab.
from urllib.error import HTTPError, URLError  # Unterscheidet Netzwerkfehler.

# ============================================================
# 1. QUELLEN, DATUM UND RECHENREGELN
# ============================================================

RECHERCHE = "25.09.2026"  # Datum der Online-Recherche, nicht Alter aller Einzeldaten.
KURSDATUM = "24.09.2026"  # Datum des verwendeten SNB-Wechselkurses.
USD_CHF = 0.8278  # 1 USD = 0.8278 CHF, SNB-Devisenkurse, 11 Uhr.
SNB_QUELLE = "https://www.snb.ch/public/rss/de/exchangeRates"  # Wechselkursquelle.
BUDGET_BASIS = "https://www.budgetyourtrip.com/"  # Gemeinsamer Teil der Budgetlinks.
WETTER_QUELLE = "https://open-meteo.com/en/docs/historical-weather-api"  # API-Dokumentation.
JAHRE = tuple(range(2021, 2026))  # Fuenf vollstaendige Vergleichsjahre: 2021 bis 2025.
STILE = ("Sparsam", "Komfort", "Luxuriös")  # Reihenfolge der recherchierten Budgetwerte.
MONATE = ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember")  # Monatsnamen.
AKTIVITAETEN = ("Strand", "Kultur", "Essen", "Natur", "Nightlife")  # Reihenfolge der Demobewertungen.

# Budget Your Trip veroeffentlicht drei Budgetklassen:
# Budget / Mid-Range / Luxury. Wir uebernehmen diese drei Werte pro Land.
# Die Spannweite bezeichnet Budget- bis Luxus-Durchschnitt, NICHT ein
# statistisches Konfidenzintervall oder das billigste/teuerste Buchungsangebot.
# Grundlage laut Anbieter: Reisendenausgaben plus Hotel-/Tourenanbieter-Daten.
# https://www.budgetyourtrip.com/howitworks.php
# Die Tageswerte enthalten bereits Unterkunft, Essen, lokale Wege und Aktivitaeten.
# Diese Positionen werden deshalb NICHT noch einmal hinzugerechnet.
# Keine erfundene Aufteilung in z.B. "45 Prozent Hotel, 30 Prozent Essen"!
# Die Kategorien der Quelle sind wegen unterschiedlicher Bezugsbasen nicht
# einfach zum Gesamttagesbudget addierbar. Internationale Anreise ist separat.
# Daten sind Laenderdurchschnitte, nicht zwingend die Preise am Klimareferenzort.
# Saison, persoenliche Buchungen und Einzelzimmer koennen deutlich abweichen.
# Fuer die Schweiz verwenden wir die originalen CHF-Werte der Quelle.
# Sonst werden die veroeffentlichten USD-Werte mit dem festen SNB-Kurs umgerechnet.
# Bereits gerundete USD-Werte koennen Umrechnungsungenauigkeiten enthalten.
# Fuer transparente Planungsrechnungen runden wir Tagesbudgets auf ganze CHF.


def ziel(land, region, ort, lat, lon, ratings, budgets, quelle, waehrung="USD") -> dict:
    """Erstellt einen Datensatz und prueft die Eingaben auf Plausibilitaet."""
    if len(ratings) != 5 or any(not 1 <= x <= 5 for x in ratings):  # Prueft alle fuenf Demobewertungen.
        raise ValueError(f"Ungültige Aktivitätswerte: {land}")  # Meldet einen Datensatzfehler.
    if len(budgets) != 3 or not 0 < budgets[0] <= budgets[1] <= budgets[2]:  # Prueft die drei Preisstufen.
        raise ValueError(f"Ungültige Budgetwerte: {land}")  # Verhindert unlogische Preisspannen.
    faktor = 1.0 if waehrung == "CHF" else USD_CHF  # CHF unveraendert lassen, USD umrechnen.
    return {  # Gibt einen benannten Datensatz statt einer schwer lesbaren Zahlenreihe zurueck.
        "land": land, "region": region, "ort": ort,  # Speichert Namen und geografische Suchgruppe.
        "lat": lat, "lon": lon,  # Speichert den Punkt fuer die historische Wetterabfrage.
        "ratings": dict(zip(AKTIVITAETEN, ratings)),  # Verbindet jede Demozahl mit ihrem Thema.
        "original": budgets, "waehrung": waehrung,  # Bewahrt die recherchierten Originalwerte auf.
        "tag": dict(zip(STILE, (round(x * faktor) for x in budgets))),  # Berechnet ganze CHF pro Tag und Stil.
        "quelle": BUDGET_BASIS + quelle,  # Verknuepft dieses Land mit seiner konkreten Budgetquelle.
    }

# ============================================================
# 2. ALLE 50 LAENDER: QUELLEN UND RECHERCHIERTE BUDGETS
# ============================================================
# Pro Eintrag: Land, Suchgruppe, Klimareferenzort, Breitengrad, Laengengrad,
# (Strand, Kultur, Essen, Natur, Nightlife), (Budget, Mittelklasse, Luxus), Quelle.
# ACHTUNG: Nur die Budgetdreiergruppen sind recherchierte Ausgabenwerte.
# Die Aktivitaets-Fuenfergruppen bleiben uebernommene, unvalidierte Demowerte.
# "Strand zwingend" bedeutet hier: mindestens 4/5 im Demo-Strandprofil.
# Das ist KEIN Nachweis eines Strandes direkt beim jeweiligen Wetterreferenzort.
# Die Suchgruppen Europa / Ausserhalb Europas dienen nur dem Reisefilter.

REISEZIELE = [
    # Portugal: Quelle 78 / 192 / 450 USD pro Person und Tag.
    ziel("Portugal", "Europa", "Lissabon", 38.72, -9.14, (5, 4, 5, 4, 4), (78, 192, 450), "portugal/trip-cost-PT"),
    # Spanien: Quelle 85 / 215 / 546 USD.
    ziel("Spanien", "Europa", "Barcelona", 41.39, 2.17, (5, 5, 5, 4, 5), (85, 215, 546), "spain"),
    # Italien: Quelle 93 / 234 / 586 USD.
    ziel("Italien", "Europa", "Rom", 41.90, 12.50, (4, 5, 5, 4, 4), (93, 234, 586), "italy/trip-cost-IT"),
    # Griechenland: Quelle 100 / 251 / 621 USD.
    ziel("Griechenland", "Europa", "Athen", 37.98, 23.73, (5, 5, 4, 4, 4), (100, 251, 621), "greece/trip-cost-GR"),
    # Kroatien: Quelle 68 / 172 / 433 USD.
    ziel("Kroatien", "Europa", "Split", 43.51, 16.44, (5, 4, 4, 5, 3), (68, 172, 433), "croatia/trip-cost-HR"),
    # Frankreich: Quelle 107 / 303 / 953 USD.
    ziel("Frankreich", "Europa", "Nizza", 43.70, 7.27, (4, 5, 5, 4, 4), (107, 303, 953), "france/trip-cost-FR"),
    # Niederlande: Quelle 99 / 247 / 612 USD.
    ziel("Niederlande", "Europa", "Amsterdam", 52.37, 4.90, (2, 5, 4, 3, 4), (99, 247, 612), "netherlands"),
    # Belgien: Quelle 80 / 197 / 468 USD.
    ziel("Belgien", "Europa", "Brüssel", 50.85, 4.35, (2, 5, 5, 3, 4), (80, 197, 468), "belgium/trip-cost-BE"),
    # Deutschland: Quelle 83 / 206 / 496 USD.
    ziel("Deutschland", "Europa", "Berlin", 52.52, 13.41, (2, 5, 4, 4, 5), (83, 206, 496), "germany/trip-cost-DE"),
    # Oesterreich: Quelle 81 / 204 / 515 USD.
    ziel("Österreich", "Europa", "Wien", 48.21, 16.37, (1, 5, 4, 5, 3), (81, 204, 515), "austria/trip-cost-AT"),
    # Schweiz: Originalwerte 123 / 296 / 695 CHF, deshalb keine USD-Umrechnung.
    ziel("Schweiz", "Europa", "Zürich", 47.38, 8.54, (1, 4, 4, 5, 3), (123, 296, 695), "switzerland/trip-cost-CH", "CHF"),
    # Island: Quelle 114 / 263 / 610 USD.
    ziel("Island", "Europa", "Reykjavík", 64.15, -21.94, (1, 3, 3, 5, 2), (114, 263, 610), "iceland/trip-cost-IS"),
    # Norwegen: Quelle 57 / 137 / 336 USD; kein garantiertes Hotel-/Buchungsbudget.
    ziel("Norwegen", "Europa", "Oslo", 59.91, 10.75, (1, 3, 4, 5, 2), (57, 137, 336), "norway/trip-cost-NO"),
    # Schweden: Quelle 75 / 182 / 424 USD.
    ziel("Schweden", "Europa", "Stockholm", 59.33, 18.07, (2, 4, 4, 5, 3), (75, 182, 424), "sweden/trip-cost-SE"),
    # Daenemark: Quelle 105 / 248 / 580 USD.
    ziel("Dänemark", "Europa", "Kopenhagen", 55.68, 12.57, (2, 4, 5, 4, 3), (105, 248, 580), "denmark/trip-cost-DK"),
    # Irland: Quelle 79 / 196 / 483 USD.
    ziel("Irland", "Europa", "Dublin", 53.35, -6.26, (2, 5, 4, 5, 4), (79, 196, 483), "ireland/trip-cost-IE"),
    # Vereinigtes Koenigreich: Quelle 96 / 245 / 630 USD.
    ziel("Vereinigtes Königreich", "Europa", "London", 51.51, -0.13, (2, 5, 5, 4, 5), (96, 245, 630), "united-kingdom/trip-cost-GB"),
    # Tschechien: Quelle 60 / 145 / 352 USD.
    ziel("Tschechien", "Europa", "Prag", 50.08, 14.44, (1, 5, 4, 4, 4), (60, 145, 352), "czech-republic/trip-cost-CZ"),
    # Polen: Quelle 31 / 80 / 208 USD.
    ziel("Polen", "Europa", "Krakau", 50.06, 19.94, (2, 5, 4, 4, 4), (31, 80, 208), "poland/trip-cost-PL"),
    # Ungarn: Quelle 46 / 117 / 301 USD.
    ziel("Ungarn", "Europa", "Budapest", 47.50, 19.04, (1, 5, 5, 3, 5), (46, 117, 301), "hungary/trip-cost-HU"),
    # Slowenien: Quelle 53 / 126 / 266 USD.
    ziel("Slowenien", "Europa", "Ljubljana", 46.06, 14.51, (2, 4, 4, 5, 2), (53, 126, 266), "slovenia/trip-cost-SI"),
    # Albanien: Quelle 51 / 123 / 300 USD.
    ziel("Albanien", "Europa", "Saranda", 39.88, 20.01, (5, 4, 4, 5, 3), (51, 123, 300), "albania/trip-cost-AL"),
    # Montenegro: Quelle 61 / 148 / 345 USD.
    ziel("Montenegro", "Europa", "Budva", 42.29, 18.84, (5, 4, 4, 5, 3), (61, 148, 345), "montenegro/trip-cost-ME"),
    # Malta: Quelle 70 / 161 / 318 USD.
    ziel("Malta", "Europa", "Valletta", 35.90, 14.51, (5, 4, 4, 3, 4), (70, 161, 318), "malta/trip-cost-MT"),
    # Zypern: Quelle 65 / 151 / 314 USD.
    ziel("Zypern", "Europa", "Larnaka", 34.92, 33.62, (5, 4, 4, 4, 4), (65, 151, 314), "cyprus/trip-cost-CY"),

    # Thailand: Quelle 35 / 97 / 292 USD.
    ziel("Thailand", "Ausserhalb Europas", "Bangkok", 13.76, 100.50, (5, 5, 5, 5, 5), (35, 97, 292), "thailand/trip-cost-TH"),
    # Vietnam: Quelle 25 / 65 / 184 USD.
    ziel("Vietnam", "Ausserhalb Europas", "Da Nang", 16.05, 108.20, (5, 5, 5, 5, 4), (25, 65, 184), "vietnam/trip-cost-VN"),
    # Indonesien: Quelle 23 / 65 / 198 USD.
    ziel("Indonesien", "Ausserhalb Europas", "Bali / Denpasar", -8.65, 115.22, (5, 4, 5, 5, 4), (23, 65, 198), "indonesia/trip-cost-ID"),
    # Japan: Quelle 54 / 137 / 346 USD.
    ziel("Japan", "Ausserhalb Europas", "Tokio", 35.68, 139.69, (3, 5, 5, 5, 4), (54, 137, 346), "japan/trip-cost-JP"),
    # Suedkorea: Quelle 49 / 125 / 318 USD.
    ziel("Südkorea", "Ausserhalb Europas", "Seoul", 37.57, 126.98, (3, 5, 5, 4, 5), (49, 125, 318), "south-korea/trip-cost-KR"),
    # Philippinen: Quelle 27 / 70 / 183 USD.
    ziel("Philippinen", "Ausserhalb Europas", "Cebu", 10.32, 123.89, (5, 4, 4, 5, 4), (27, 70, 183), "philippines/trip-cost-PH"),
    # Sri Lanka: Quelle 20 / 56 / 167 USD.
    ziel("Sri Lanka", "Ausserhalb Europas", "Colombo", 6.93, 79.85, (5, 5, 5, 5, 3), (20, 56, 167), "sri-lanka/trip-cost-LK"),
    # Malaysia: Quelle 37 / 104 / 322 USD.
    ziel("Malaysia", "Ausserhalb Europas", "Kuala Lumpur", 3.14, 101.69, (5, 4, 5, 5, 4), (37, 104, 322), "malaysia/trip-cost-MY"),
    # Singapur: Quelle 70 / 182 / 495 USD.
    ziel("Singapur", "Ausserhalb Europas", "Singapur", 1.35, 103.82, (2, 5, 5, 2, 5), (70, 182, 495), "singapore/trip-cost-SG"),
    # Indien: Quelle 15 / 40 / 111 USD.
    ziel("Indien", "Ausserhalb Europas", "Neu-Delhi", 28.61, 77.21, (3, 5, 5, 5, 4), (15, 40, 111), "india/trip-cost-IN"),
    # Nepal: Quelle 14 / 39 / 117 USD.
    ziel("Nepal", "Ausserhalb Europas", "Kathmandu", 27.72, 85.32, (1, 5, 4, 5, 2), (14, 39, 117), "nepal/trip-cost-NP"),
    # Marokko: Quelle 34 / 89 / 240 USD.
    ziel("Marokko", "Ausserhalb Europas", "Marrakesch", 31.63, -8.00, (3, 5, 5, 4, 3), (34, 89, 240), "morocco/trip-cost-MA"),
    # Aegypten: Quelle 16 / 38 / 87 USD; kein Versprechen fuer Luxusresorts.
    ziel("Ägypten", "Ausserhalb Europas", "Hurghada", 27.26, 33.81, (5, 5, 4, 4, 3), (16, 38, 87), "egypt/trip-cost-EG"),
    # Suedafrika: Quelle 47 / 119 / 308 USD.
    ziel("Südafrika", "Ausserhalb Europas", "Kapstadt", -33.93, 18.42, (4, 4, 5, 5, 4), (47, 119, 308), "south-africa/trip-cost-ZA"),
    # Tansania: Quelle 42 / 109 / 298 USD; spezielle Safaris gesondert kalkulieren.
    ziel("Tansania", "Ausserhalb Europas", "Sansibar", -6.17, 39.20, (5, 4, 4, 5, 2), (42, 109, 298), "tanzania/trip-cost-TZ"),
    # Kenia: Quelle 59 / 140 / 300 USD; spezielle Safaris gesondert kalkulieren.
    ziel("Kenia", "Ausserhalb Europas", "Mombasa", -4.05, 39.67, (4, 4, 4, 5, 3), (59, 140, 300), "kenya/trip-cost-KE"),
    # Mexiko: Quelle 53 / 148 / 456 USD.
    ziel("Mexiko", "Ausserhalb Europas", "Cancún", 21.16, -86.85, (5, 5, 5, 4, 5), (53, 148, 456), "mexico/trip-cost-MX"),
    # Costa Rica: Quelle 60 / 152 / 379 USD.
    ziel("Costa Rica", "Ausserhalb Europas", "San José", 9.93, -84.08, (5, 3, 4, 5, 3), (60, 152, 379), "costa-rica/trip-cost-CR"),
    # Kolumbien: Quelle 24 / 67 / 212 USD.
    ziel("Kolumbien", "Ausserhalb Europas", "Cartagena", 10.39, -75.48, (4, 5, 5, 5, 5), (24, 67, 212), "colombia/trip-cost-CO"),
    # Brasilien: Quelle 37 / 97 / 271 USD.
    ziel("Brasilien", "Ausserhalb Europas", "Rio de Janeiro", -22.91, -43.17, (5, 5, 5, 5, 5), (37, 97, 271), "brazil/trip-cost-BR"),
    # Peru: Quelle 29 / 78 / 233 USD.
    ziel("Peru", "Ausserhalb Europas", "Lima", -12.05, -77.04, (2, 5, 5, 5, 3), (29, 78, 233), "peru/trip-cost-PE"),
    # Argentinien: Quelle 28 / 65 / 133 USD; Anbieter warnt vor Waehrungsschwankungen.
    ziel("Argentinien", "Ausserhalb Europas", "Buenos Aires", -34.60, -58.38, (4, 5, 5, 5, 5), (28, 65, 133), "argentina/trip-cost-AR"),
    # Vereinigte Staaten: Quelle 121 / 324 / 925 USD.
    ziel("Vereinigte Staaten", "Ausserhalb Europas", "Los Angeles", 34.05, -118.24, (4, 5, 5, 5, 5), (121, 324, 925), "united-states-of-america/trip-cost-US"),
    # Kanada: Quelle 71 / 197 / 594 USD.
    ziel("Kanada", "Ausserhalb Europas", "Vancouver", 49.28, -123.12, (2, 4, 4, 5, 3), (71, 197, 594), "canada/trip-cost-CA"),
    # Australien: Quelle 73 / 190 / 501 USD.
    ziel("Australien", "Ausserhalb Europas", "Sydney", -33.87, 151.21, (5, 4, 5, 5, 5), (73, 190, 501), "australia"),
]

# ============================================================
# 3. BUDGETBERECHNUNG
# ============================================================


def chf(betrag: float) -> str:
    return "CHF " + f"{betrag:,.0f}".replace(",", "'")  # Formatiert z.B. CHF 1'500.


def budgetrechnung(z: dict, stil: str, p: dict) -> dict:
    """Berechnet eine transparente Schaetzung fuer eine Person."""
    tageswert = z["tag"][stil]  # Waehlt den recherchierten Wert des ausgewaehlten Reisestils.
    vor_ort = tageswert * p["tage"]  # Quelle ist pro Reisetag, deshalb NICHT nochmals Hotelnaechte addieren.
    basis = vor_ort + p["anreise"] + p["extras"]  # Addiert nur separat eingegebene, nicht enthaltene Ausgaben.
    reserve = math.ceil(basis * p["reserve"] / 100)  # Nutzergewaehlte Reserve, auf ganze CHF aufgerundet.
    return {  # Bewahrt alle Zwischenwerte fuer die Kostenaufschluesselung auf.
        "tag": tageswert, "vor_ort": vor_ort, "anreise": p["anreise"],
        "extras": p["extras"], "basis": basis, "reserve": reserve,
        "gesamt": basis + reserve,  # Dieser Planungsbetrag wird mit dem Maximalbudget verglichen.
    }

# Rechenbeispiel mit Malta und Sparsam:
# round(70 USD * 0.8278) = 58 CHF/Tag.
# 10 Tage * 58 CHF = 580 CHF vor Ort.
# Eigene Anreiseannahme 200 CHF + Extras 0 CHF => Basis 780 CHF.
# Vom Nutzer gewaehlt: 15 Prozent Reserve => 117 CHF.
# Geschätzter Planungsbetrag = 897 CHF.
# Der Bereich 780 bis 897 CHF ist Basis bis Basis+Reserve, NICHT ein
# aus der Quelle ermitteltes statistisches Unsicherheitsintervall.
# Budget-MUSS prueft 897 CHF. Geringere Ausgaben werden nicht bestraft.
# Ein hoher Reisestil wird niemals automatisch auf Sparsam umgestellt.
# Solo ist keine Preisklasse: Alleinreisende koennen alle Stile auswaehlen.
# Ein bekanntes Einzelzimmer-Mehrbudget kann in "Extras" eingetragen werden.

# ============================================================
# 4. TEMPERATURDATEN MIT PRUEFUNG UND ZWISCHENSPEICHER
# ============================================================


def monatsmittel(wetter: dict) -> dict:
    """Berechnet je Monat den Mittelwert der fuenf einzelnen Jahresmittel."""
    daily = wetter.get("daily", {})  # Liest den Block mit Tagesdaten.
    daten = daily.get("time", [])  # Liest Datumsangaben.
    werte = daily.get("temperature_2m_mean", [])  # Liest mittlere 2-m-Lufttemperaturen.
    if len(daten) != len(werte) or not daten:  # Stellt eine eindeutige Datum-Wert-Zuordnung sicher.
        raise ValueError("Unvollständige Wetterantwort.")  # Verhindert falsche Zuordnungen.
    gruppen = {}  # Sammelt Tage getrennt nach Jahr und Monat.
    for datum, wert in zip(daten, werte):  # Durchlaeuft Datum und zugehoerigen Temperaturwert.
        if wert is None or not isinstance(wert, (int, float)) or not math.isfinite(wert):  # Erkennt Datenluecken.
            continue  # Erfindet fuer fehlende Tage keinen Ersatzwert.
        jahr, monat, _ = map(int, datum.split("-"))  # Liest Jahr und Monat aus ISO-Datum.
        if jahr in JAHRE:  # Verwendet nur den festgelegten Zeitraum.
            gruppen.setdefault((jahr, monat), []).append(float(wert))  # Ordnet den Tageswert ein.
    mittelwerte = {}  # Speichert ausreichend belegte Monatswerte.
    for monat in range(1, 13):  # Prueft alle zwoelf Monate.
        jahresmittel = []  # Jeder Jahrgang soll gleiches Gewicht erhalten.
        for jahr in JAHRE:  # Durchlaeuft die fuenf Vergleichsjahre.
            tage = gruppen.get((jahr, monat), [])  # Holt vorhandene Tage dieses Monats.
            soll = calendar.monthrange(jahr, monat)[1]  # Berechnet die erwartete Tagesanzahl.
            if len(tage) >= math.ceil(soll * 0.95):  # Verlangt mindestens 95 Prozent Datenabdeckung.
                jahresmittel.append(sum(tage) / len(tage))  # Berechnet das Monatsmittel dieses Jahres.
        if len(jahresmittel) == len(JAHRE):  # Akzeptiert nur Monate mit allen fuenf Jahren.
            mittelwerte[monat] = sum(jahresmittel) / len(jahresmittel)  # Gewichtet jedes Jahr gleich.
    return mittelwerte  # Laesst unzureichend belegte Monate bewusst weg.


@st.cache_data(ttl=2592000, show_spinner=False, max_entries=20)  # Behaelt historische Werte bis zu 30 Tage.
def lade_wetterblock(orte: tuple) -> dict:
    """Laedt maximal zehn Orte pro Anfrage und berechnet alle Monatswerte."""
    parameter = {  # Definiert ausschliesslich dokumentierte API-Parameter.
        "latitude": ",".join(str(o[1]) for o in orte),  # Koordinaten in derselben Reihenfolge wie Namen.
        "longitude": ",".join(str(o[2]) for o in orte),  # Passende Laengengrade.
        "start_date": "2021-01-01", "end_date": "2025-12-31",  # Fester historischer Zeitraum.
        "daily": "temperature_2m_mean",  # Tagesmittel, nicht Tageshoechsttemperatur.
        "timezone": "auto", "temperature_unit": "celsius", "models": "era5",  # Konsistente Reanalyse.
    }
    url = "https://archive-api.open-meteo.com/v1/archive?" + urlencode(parameter)  # Baut die Anfrage.
    anfrage = Request(url, headers={"User-Agent": "TravelMatch-StudyPrototype/2.0"})  # Kennzeichnet den Aufruf.
    with urlopen(anfrage, timeout=25) as antwort:  # Begrenzt die Wartezeit pro Anfrage.
        daten = json.loads(antwort.read().decode("utf-8"))  # Dekodiert die Wetterantwort.
    if isinstance(daten, dict) and daten.get("error"):  # Erkennt eine API-Fehlermeldung.
        raise ValueError(daten.get("reason", "Wetterdienst meldet einen Fehler."))  # Reicht die Ursache weiter.
    daten = [daten] if isinstance(daten, dict) else daten  # Vereinheitlicht Einzel- und Mehrfachantworten.
    if not isinstance(daten, list) or len(daten) != len(orte):  # Prueft die Anzahl der Orte.
        raise ValueError("Anzahl der Wetterorte stimmt nicht mit der Anfrage überein.")  # Stoppt Fehlzuordnung.
    ausgabe = {}  # Legt die Ergebnissammlung an.
    for ort, wetter in zip(orte, daten):  # Ordnet jeden Antwortblock seinem Anfrageort zu.
        if wetter.get("daily_units", {}).get("temperature_2m_mean") != "°C":  # Kontrolliert die Einheit.
            raise ValueError("Unerwartete Temperatureinheit.")  # Verhindert Fahrenheit als Celsius.
        ausgabe[ort[0]] = monatsmittel(wetter)  # Speichert zwoelf moegliche Monatswerte pro Land.
    return ausgabe  # Cache speichert nur erfolgreich verarbeitete Antworten.

# Die Anwendung laedt feste Zehnerbloecke und nutzt sie auch nach einer
# Aenderung von Monat, Stil oder Budget weiter. So werden grosse identische
# Wetterabfragen nicht bei jeder Sliderbewegung erneut gesendet.
# Der Fuenfjahresmittelwert ist KEINE 30-jaehrige Klimanorm und keine Garantie
# fuer zukuenftiges Wetter. Ein Referenzort repraesentiert nicht das ganze Land.

# ============================================================
# 5. FILTER UND NACHVOLLZIEHBARE PASSUNG
# ============================================================


def vorfiltern(p: dict) -> list:
    kandidaten = []  # Startet mit einer leeren Kandidatenliste.
    for z in REISEZIELE:  # Prueft alle fuenfzig Laender.
        if p["region"] != "Egal" and z["region"] != p["region"]:  # Wendet den Regionsfilter an.
            continue  # Laesst eine nicht gewuenschte Region weg.
        if p["strand_muss"] and z["ratings"]["Strand"] < 4:  # Nutzt die deklarierte Demo-Strandschwelle.
            continue  # Schliesst geringe Strandeignung aus.
        kosten = budgetrechnung(z, p["stil"], p)  # Rechnet mit genau dem ausgewaehlten Reisestil.
        if p["budget_muss"] and kosten["gesamt"] > p["budget"]:  # Prueft die Schaetzung inklusive Reserve.
            continue  # Schliesst Ueberschreitung aus; wechselt nicht heimlich den Stil.
        kandidaten.append({**z, "rechnung": kosten})  # Kopiert Land und berechnete Kosten.
    return kandidaten  # Liefert nur Kandidaten, die die bisherigen Muss-Kriterien erfuellen.


def passung(z: dict, p: dict) -> tuple:
    """Berechnet einen erklaerbaren Distanzscore, keine Wahrscheinlichkeit."""
    faktoren = []  # Hier werden Kriterium, Gewicht und Abweichung gespeichert.
    for thema, wichtigkeit in p["interessen"].items():  # Nimmt jeden Wichtigkeitsregler auf.
        gewicht = (wichtigkeit - 1) / 4  # 1 wird 0: unwichtig ignorieren; 5 wird 1: volles Gewicht.
        abweichung = (5 - z["ratings"][thema]) / 4  # Abstand zur bestmoeglichen Eignung, 0 bis 1.
        faktoren.append((thema, gewicht, abweichung))  # Speichert den Beitrag fuer die Erklaerung.
    if p["temperatur_nutzen"]:  # Nimmt Temperatur nur nach ausdruecklicher Auswahl in den Score auf.
        abweichung = min(abs(z["temperatur"] - p["temperatur"]) / 20, 1.0)  # 20 Grad Abweichung = volle Distanz.
        faktoren.append(("Temperatur", 1.0, abweichung))  # Festes, offengelegtes Gewicht wie ein 5/5-Interesse.
    if not p["budget_muss"]:  # Ein weiches Budget darf ueberschritten werden, wird dann aber abgewertet.
        mehrkosten = max(0, z["rechnung"]["gesamt"] - p["budget"])  # Niedrigere Kosten werden NICHT bestraft.
        faktoren.append(("Budget", 1.0, min(mehrkosten / p["budget"], 1.0)))  # Misst relative Ueberschreitung.
    gewichtsumme = sum(g for _, g, _ in faktoren)  # Ermittelt das Gesamtgewicht aktiver Kriterien.
    if gewichtsumme == 0:  # Ohne aktive Praeferenzen ist keine sinnvolle Passung berechenbar.
        return None, []  # Verhindert Division durch null und erfundene 100 Punkte.
    d2 = sum(g * a * a for _, g, a in faktoren) / gewichtsumme  # Gewichtete mittlere quadratische Abweichung.
    score = 100 * (1 - math.sqrt(d2))  # Macht Distanz 0 zu 100 und Distanz 1 zu 0 Punkten.
    details = [  # Baut die Tabelle, die dem Nutzer den Score erklaert.
        {"Kriterium": name, "Gewicht im Score": f"{100 * g / gewichtsumme:.1f} %",
         "Einzelpassung": f"{100 * (1 - a):.0f}/100", "Gewichtete Abweichung²": round(g * a * a / gewichtsumme, 4)}
        for name, g, a in faktoren  # Zeigt auch ignorierte Kriterien mit Gewicht null.
    ]
    return round(max(0, min(100, score)), 1), details  # Begrenzt reine Rundungsartefakte.

# BESSER ALS DER ALTE CODE:
# "Essen unwichtig" bedeutet nicht mehr "suche Laender mit schlechtem Essen".
# Wichtigkeit wird als GEWICHT verwendet, nicht als gewuenschte Angebotsqualitaet.
# Die Aktivitaets-Zielwerte sind 5/5 fuer jedes beachtete Thema.
# Temperatur 20 Grad ist eine dokumentierte Modellentscheidung, nicht gelernt.
# Die Formel ist eine gewichtete, normierte euklidische Distanz zum Idealprofil.
# Der Score verwendet keinen willkuerlichen Anzeige-Multiplikator wie "mal 30".
# Trotzdem bleiben Auswahl, Gewichte und Demo-Ratings nicht empirisch validiert.

# ============================================================
# 6. BENUTZEROBERFLAECHE
# ============================================================


def app() -> None:
    st.set_page_config(page_title="TravelMatch", page_icon="🌍", layout="wide")  # Browser und Seitenbreite.
    st.title("TravelMatch")  # Zeigt den Namen ohne problematische Flaggenkuerzel.
    st.write("Wohin passen deine Wünsche – und dein Budget?")  # Gibt der Seite eine kurze Einleitung.
    st.caption(f"50 Länder · Drei Reisestile · Budgetquellen geprüft am {RECHERCHE}")  # Versions-/Datenhinweis.

    with st.form("reiseplanung"):  # Sammelt alle Eingaben, bevor eine Suche gestartet wird.
        st.subheader("1. Deine Reise")  # Trennt Reiseangaben vom Reisestil.
        links, mitte, rechts = st.columns(3)  # Ordnet die Felder nebeneinander an.
        with links:  # Felder zur Reisezeit.
            monat = st.selectbox("Reisemonat", MONATE)  # Waehlt den Kalendermonat.
            tage = st.slider("Reisetage vor Ort", 3, 45, 10)  # Zaehlt die Tage, auf die der Tagesrichtwert angewandt wird.
        with mitte:  # Felder zum finanziellen Rahmen.
            budget = st.number_input("Maximalbudget pro Person in CHF", min_value=100, max_value=100000, value=2000, step=100)  # Exakte Eingabe.
            budget_muss = st.checkbox("Budget darf nicht überschritten werden", value=True)  # Aktiviert den harten Filter.
        with rechts:  # Feld zum geografischen Suchgebiet.
            region = st.selectbox("Region", ("Egal", "Europa", "Ausserhalb Europas"))  # Filtert die Suchgruppe.
            reserve = st.slider("Zusätzliche Planungsreserve (%)", 0, 40, 15, step=5)  # Freie Annahme des Nutzers, kein Quellenwert.

        st.subheader("2. Wie möchtest du reisen?")  # Leitet das Reisestil-Raster ein.
        stil = st.radio("Dein Reisestil", STILE, index=0, horizontal=True)  # Waehlt einen der drei echten Quellwerte.
        karten = st.columns(3)  # Erstellt drei native Karten statt HTML-Konstruktionen.
        beschreibungen = ("Hostel oder einfache Unterkunft, günstige Mahlzeiten und lokale Verkehrsmittel.", "Mittelklasse-Unterkunft, reguläre Restaurants und mehr bezahlte Unternehmungen.", "Gehobene Unterkünfte, anspruchsvollere Restaurants und exklusivere Erlebnisse.")  # Beschreibt die Kategorien.
        for karte, name, text in zip(karten, STILE, beschreibungen):  # Fuellt jede Stilkarte.
            with karte:  # Waehlt die entsprechende Spalte.
                with st.container(border=True):  # Erzeugt einen zuverlaessigen Rahmen ohne HTML.
                    st.markdown(f"**{name}**")  # Nennt den Stil.
                    st.write(text)  # Erklaert den Stil.
        st.caption("Alle Angaben pro Person. Allein reisen ist kein Reisestil: Du kannst solo sparsam oder luxuriös reisen. Ein bekanntes Einzelzimmer-Mehrbudget trägst du unten als Zusatzkosten ein.")  # Trennt Reisestil von Reisebegleitung.

        with st.expander("Anreise und zusätzliche Ausgaben einplanen", expanded=True):  # Zeigt die echte Aufschluesselung.
            c1, c2 = st.columns(2)  # Ordnet die beiden Extra-Budgetfelder.
            with c1:  # Eingabe der Anreiseannahme.
                anreise = st.number_input("Hin- und Rückreise pro Person (CHF)", min_value=0, max_value=30000, value=0, step=50)  # Kein erfundener Flugpreis.
            with c2:  # Eingabe individueller zusaetzlicher Kosten.
                extras = st.number_input("Zusatzkosten pro Person, insgesamt (CHF)", min_value=0, max_value=30000, value=0, step=50)  # Z.B. Einzelzimmer-Aufpreis, Visum, Safari.
            st.caption("Deine Anreiseannahme gilt im Vergleich für alle Länder. 0 CHF bedeutet: Anreise noch nicht eingerechnet. Zusatzkosten nur für Ausgaben erfassen, die nicht bereits im Tagesbudget enthalten sind.")  # Verhindert falsche Interpretation.

        st.subheader("3. Temperatur und Interessen")  # Leitet die Praeferenzen ein.
        t1, t2, t3 = st.columns(3)  # Drei Spalten fuer Wetteroptionen.
        with t1:  # Gewuenschte Temperatur.
            temperatur = st.slider("Gewünschtes Monatsmittel (°C)", -5, 35, 25)  # Korrektes Slider-Argument, kein unit-Parameter.
            temperatur_nutzen = st.checkbox("Temperatur berücksichtigen", value=True)  # Erlaubt auch eine reine Budget-/Interessensuche.
        with t2:  # Zwingende Temperaturauswahl.
            temperatur_muss = st.checkbox("Temperatur muss ungefähr passen")  # Optionaler harter Wetterfilter.
            toleranz = st.slider("Erlaubte Abweichung bei Muss (°C)", 1, 10, 4)  # Toleranz wirkt nur bei aktiviertem Muss.
        with t3:  # Zwingende Strandoption.
            strand_muss = st.checkbox("Strand muss vorhanden sein")  # Ergaenzt den weiterhin vorhandenen Strandregler.
            st.caption("Strand-Muss wählt ausgeprägte Strandziele im hinterlegten Länderprofil. Der Wetterreferenzort kann anderswo liegen.")  # Nennt die Datengrenze.

        st.caption("1 = unwichtig, 5 = sehr wichtig. Ein unwichtiges Thema beeinflusst den Match nicht.")  # Erklaert die korrigierte Gewichtungslogik.
        interessen = {}  # Speichert die fuenf Wichtigkeiten.
        spalten = st.columns(5)  # Ordnet die Wichtigkeitsregler an.
        for spalte, thema in zip(spalten, AKTIVITAETEN):  # Erstellt jeden Regler genau einmal.
            with spalte:  # Positioniert das Eingabeelement.
                interessen[thema] = st.slider(thema, 1, 5, 2 if thema == "Nightlife" else 3)  # Setzt moderate Startwerte.
        abgesendet = st.form_submit_button("Passende Reiseziele finden", type="primary")  # Ein Klick startet die Berechnung.

    # Diese Uebersicht ist auch bei einem Ausfall der Wetter-API verfuegbar.
    with st.expander("Budgetraster aller 50 Länder mit Quellen"):  # Macht die recherchierten Werte kontrollierbar.
        st.caption("Ca. CHF pro Person und Tag: Unterkunft, Essen, lokale Wege und Aktivitäten. Spanne = Budget- bis Luxus-Durchschnitt, kein garantiertes Minimum oder Maximum.")  # Definiert die Spannweite.
        zeilen = [{"Land": z["land"], **z["tag"], "Budgetspanne CHF/Tag": f"{z['tag'][STILE[0]]} bis {z['tag'][STILE[2]]}", "Quelle": z["quelle"]} for z in REISEZIELE]  # Erstellt 50 Tabellenzeilen.
        st.dataframe(zeilen, hide_index=True, use_container_width=True)  # Zeigt das verlangte Raster.
        st.caption(f"USD-Umrechnung: 1 USD = {USD_CHF} CHF, SNB {KURSDATUM}. Tageswerte auf ganze CHF gerundet. Quellenabruf {RECHERCHE}; zugrunde liegende Reisendenausgaben können älter sein.")  # Dokumentiert Stand und Rundung.

    if not abgesendet:  # Vor dem ersten Klick werden noch keine Wetterabfragen ausgefuehrt.
        return  # Laesst die Eingabeseite stehen.
    if temperatur_muss and not temperatur_nutzen:  # Erkennt widerspruechliche Wetterauswahl.
        st.warning("Aktiviere auch 'Temperatur berücksichtigen', damit dein Temperatur-Muss geprüft werden kann.")  # Gibt eine konkrete Korrektur.
        return  # Verhindert eine scheinbar gepruefte Pflichtbedingung.

    p = {  # Fasst alle Eingaben fuer die Rechenfunktionen zusammen.
        "monat": MONATE.index(monat) + 1, "tage": tage, "budget": budget, "stil": stil,
        "region": region, "reserve": reserve, "anreise": anreise, "extras": extras,
        "budget_muss": budget_muss, "strand_muss": strand_muss,
        "temperatur": temperatur, "temperatur_nutzen": temperatur_nutzen,
        "temperatur_muss": temperatur_muss, "toleranz": toleranz, "interessen": interessen,
    }
    kandidaten = vorfiltern(p)  # Wendet Region, gewaehlten Stil, Budget und Strand-Muss an.
    if not kandidaten:  # Behandelt eine leere Treffermenge vor der Wetterabfrage.
        st.info("Kein Land passt für diesen Reisestil in deine Muss-Kriterien. Passe Budget, Reisedauer, Region oder Reisestil an. Die Reserve wird beim Budget mitgerechnet.")  # Erklaert den Grund.
        return  # Spart unnoetige API-Aufrufe.

    if temperatur_nutzen:  # Laedt nur bei gewuenschtem Temperaturvergleich historische Daten.
        alle_temperaturen, probleme = {}, []  # Trennt erfolgreiche Daten von fehlgeschlagenen Bloecken.
        benoetigt = {z["land"] for z in kandidaten}  # Merkt sich die verbleibenden Laender.
        with st.spinner("Historische Monatswerte werden geladen. Der erste Abruf kann etwas dauern..."):  # Zeigt Wartefeedback.
            for start in range(0, len(REISEZIELE), 10):  # Nutzt stabile Zehnerbloecke fuer Wiederverwendung des Caches.
                block = REISEZIELE[start:start + 10]  # Nimmt maximal zehn Referenzorte.
                if not any(z["land"] in benoetigt for z in block):  # Prueft, ob der Block ueberhaupt gebraucht wird.
                    continue  # Ueberspringt unnoetige Orte.
                orte = tuple((z["land"], z["lat"], z["lon"]) for z in block)  # Erzeugt stabile Cache-Argumente.
                try:  # Faengt Netzwerk- und Datenformatfehler ab.
                    alle_temperaturen.update(lade_wetterblock(orte))  # Uebernimmt erfolgreiche Monatswerte.
                except (HTTPError, URLError, TimeoutError, OSError, ValueError, TypeError, KeyError) as fehler:  # Behandelt erwartbare API-Probleme.
                    probleme.append(type(fehler).__name__)  # Speichert nur den Fehlertyp, keine privaten Details.
        mit_wetter = []  # Bereitet eine Liste ohne erfundene Temperaturwerte vor.
        fehlend = []  # Merkt sich ausgeschlossene Laender mit Datenluecken.
        for z in kandidaten:  # Ordnet den angefragten Monatswert zu.
            wert = alle_temperaturen.get(z["land"], {}).get(p["monat"])  # Liest nur den ausgewaehlten Monat.
            if wert is None:  # Fehlende Daten sind nicht dasselbe wie 0 Grad.
                fehlend.append(z["land"])  # Dokumentiert die Einschraenkung.
            else:  # Mit valider Temperatur kann das Land verglichen werden.
                mit_wetter.append({**z, "temperatur": wert})  # Behaelt ungerundete Werte fuer Filter und Score.
        kandidaten = mit_wetter  # Verwendet ausschliesslich belegt verfuegbare Temperaturen.
        if fehlend:  # Meldet eingeschraenkte Abdeckung transparent.
            st.warning("Wetterdaten fehlen für: " + ", ".join(fehlend) + ". Diese Länder fehlen im Temperaturvergleich. Du kannst die Temperaturwahl deaktivieren und neu suchen.")  # Bietet eine funktionierende Alternative.
        if temperatur_muss:  # Prueft jetzt erst den zwingenden Temperaturbereich.
            kandidaten = [z for z in kandidaten if abs(z["temperatur"] - temperatur) <= toleranz]  # Filtert ohne Rundungsfehler.
    if not kandidaten:  # Erkennt auch leere Ergebnisse nach Wetterfilter oder API-Ausfall.
        st.info("Kein verbleibendes Ziel mit passenden, verfügbaren Temperaturdaten. Passe die Temperaturvorgabe an oder suche ohne Temperaturvergleich.")  # Kein Absturz, keine Ersatztemperaturen.
        return  # Stoppt nur die aktuelle Suche.

    for z in kandidaten:  # Berechnet die Passung fuer jedes passende Land.
        z["score"], z["details"] = passung(z, p)  # Speichert Wert und nachvollziehbare Zerlegung.
    kandidaten.sort(key=lambda z: (-(z["score"] if z["score"] is not None else -1), z["rechnung"]["gesamt"], z["land"]))  # Beste Passung zuerst, bei Gleichstand guenstiger.
    st.divider()  # Trennt Eingaben und Ergebnisse.
    st.header("Deine passenden Reiseziele")  # Keine Flaggen, keine Landeskuerzel.
    st.write(f"**{stil} · {tage} Tage · {monat} · Budget {chf(budget)} pro Person**")  # Bestaetigt das verwendete Suchprofil.
    st.caption(f"{len(kandidaten)} passende Länder; angezeigt werden die besten fünf. Budgetprüfung inklusive deiner {reserve} % Reserve.")  # Erklaert Filter und Begrenzung.
    if anreise == 0:  # Warnt auch in den Ergebnissen vor unvollstaendiger Gesamtreiseschaetzung.
        st.info("An- und Abreise sind noch nicht eingerechnet. Die Beträge sind deshalb kein vollständiges Reiseangebot.")  # Vermeidet falsche Gesamtpreisversprechen.

    for position, z in enumerate(kandidaten[:5], 1):  # Zeigt die maximal fuenf besten Vorschlaege.
        rechnung = z["rechnung"]  # Holt die bereits berechneten Kosten.
        with st.container(border=True):  # Native, im hellen und dunklen Theme lesbare Ergebniskarte.
            st.subheader(f"{position}. {z['land']}")  # Nennt ausschliesslich Rang und deutschen Laendernamen.
            if z["score"] is not None:  # Zeigt nur bei vorhandenen Praeferenzen einen Score.
                st.write(f"**{z['score']:.1f} von 100 Passungspunkten**")  # Nennt Punkte statt Erfolgswahrscheinlichkeit.
                st.progress(z["score"] / 100)  # Visualisiert den Score auf einer Skala von 0 bis 1.
            else:  # Ohne aktive Kriterien ist die Reihenfolge ein Preisvergleich.
                st.caption("Keine gewichteten Wünsche gewählt: nach geschätzten Kosten sortiert.")  # Erfindet keinen Match.
            a, b, c = st.columns(3)  # Ordnet die wichtigsten Kennzahlen an.
            a.metric("Geschätzt vor Ort / Tag", chf(rechnung["tag"]))  # Tageswert des ausgewaehlten Stils.
            b.metric("Geschätztes Planungsbudget", chf(rechnung["gesamt"]))  # Beinhaltet explizite Extras und Reserve.
            if temperatur_nutzen:  # Nur reale geladene Temperaturen darstellen.
                c.metric(f"Monatsmittel {monat}", f"{z['temperatur']:.1f} °C")  # Rundet nur fuer die Anzeige.
                st.caption(f"Wetterreferenz {z['ort']}: Mittel 2021–2025, keine Vorhersage. Budgetwerte gelten landesweit.")  # Grenzt die Aussage ein.
            else:  # Ohne Temperatur eine alternative Kennzahl zeigen.
                c.metric("Spielraum zum Budget", chf(budget - rechnung["gesamt"]))  # Gibt verbleibendes Budget an.

            st.markdown("**Recherchiertes Budgetraster**")  # Zeigt alle Stile, nicht nur den ausgewaehlten.
            stilzeilen = []  # Sammelt die drei vergleichbaren Stilrechnungen.
            for s in STILE:  # Berechnet fuer dieses Land jeden der drei Reisestile.
                r = budgetrechnung(z, s, p)  # Nutzt dieselben Tage und persoenlichen Zusatzannahmen.
                stilzeilen.append({"Reisestil": s + (" (deine Wahl)" if s == stil else ""), "Ca. CHF / Tag vor Ort": r["tag"], "Ca. CHF vor Ort gesamt": r["vor_ort"], "CHF inkl. Eingaben + Reserve": r["gesamt"]})  # Zeigt alle Vergleichswerte.
            st.table(stilzeilen)  # Gibt das Raster ohne kaputtes HTML aus.
            st.caption(f"Budget- bis Luxus-Richtwert: {chf(z['tag'][STILE[0]])} bis {chf(z['tag'][STILE[2]])} pro Tag. Kein garantierter Mindest- oder Höchstpreis.")  # Beschreibt die Spannweite korrekt.

            with st.expander("So entsteht dein geschätztes Budget", expanded=True):  # Zeigt die nachvollziehbare Rechnung.
                st.write(f"Vor Ort: **{tage} Tage × {chf(rechnung['tag'])} = {chf(rechnung['vor_ort'])}**")  # Macht Multiplikation sichtbar.
                st.caption("Darin enthalten: Unterkunft, Essen, lokale Mobilität und Aktivitäten. Keine erfundene prozentuale Aufteilung.")  # Verhindert Doppelzaehlung.
                st.table([  # Einzelne nachweisbare/selbst gewaehlte Summanden.
                    {"Posten": "Vor Ort (Quellenrichtwert)", "CHF": rechnung["vor_ort"]},
                    {"Posten": "Hin- und Rückreise (deine Eingabe)", "CHF": rechnung["anreise"]},
                    {"Posten": "Zusatzkosten (deine Eingabe)", "CHF": rechnung["extras"]},
                    {"Posten": f"Planungsreserve {reserve} % (deine Wahl)", "CHF": rechnung["reserve"]},
                    {"Posten": "Geschätztes Planungsbudget", "CHF": rechnung["gesamt"]},
                ])
                st.caption(f"Basis ohne Reserve: {chf(rechnung['basis'])}. Mit Reserve: {chf(rechnung['gesamt'])}. Das ist ein Planungsszenario, kein statistisch gemessener Preisbereich.")  # Trennt Daten und Annahme.

            differenz = budget - rechnung["gesamt"]  # Vergleicht die Gesamtschaetzung mit dem Nutzerbudget.
            if differenz >= 0:  # Positiver Spielraum.
                st.success(f"Nach dieser Schätzung bleiben {chf(differenz)} innerhalb deines Budgets.")  # Kein Preisversprechen.
            else:  # Nur bei nicht zwingendem Budget moeglich.
                st.warning(f"Die Schätzung liegt {chf(-differenz)} über deinem Budget.")  # Zeigt genaue Ueberschreitung.
            if z["land"] == "Argentinien":  # Nimmt die besondere Warnung der Quelle auf.
                st.caption("Die Budgetquelle weist für Argentinien ausdrücklich auf Währungsschwankungen hin. Aktuelle Buchungsangebote gegenprüfen.")  # Keine Scheingenauigkeit.

            with st.expander("Warum passt dieses Reiseziel?"):  # Versteckt keine relevanten Scorefaktoren.
                st.write("**Deine Wichtigkeiten und das hinterlegte Angebotsprofil:**")  # Leitet das persoenliche Matching ein.
                st.table([{"Thema": t, "Dir wichtig (1–5)": interessen[t], "Angebotsprofil (Demo, 1–5)": z["ratings"][t]} for t in AKTIVITAETEN])  # Trennt Wunschgewicht und Qualitaetsrating.
                st.table(z["details"])  # Zeigt jedes Gewicht und jede berechnete Teilabweichung.
                st.caption("Unwichtige Themen werden ignoriert. Mehr passende Angebote helfen bei wichtigen Themen. Unter deinem Budget zu bleiben verschlechtert die Passung nicht. Aktivitätsprofile sind noch unvalidierte Beispielbewertungen.")  # Wichtige Nutzerinterpretation, keine lange Methodik.
            st.markdown(f"[Budgetquelle für {z['land']}: Budget Your Trip]({z['quelle']})")  # Direkte Quellenzuordnung je Ergebnis.
            if temperatur_nutzen:  # Attribution fuer die genutzten Wetterdaten.
                st.markdown(f"[Historische Wetterdaten: Open-Meteo / ERA5]({WETTER_QUELLE})")  # Verlinkt die primaere Wetterdokumentation.


if __name__ == "__main__":  # Startet die Oberflaeche bei Streamlit; Funktionen bleiben separat testbar.
    app()  # Fuehrt die komplette App aus.
