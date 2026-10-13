#!/usr/bin/env python3
"""Static site build for dasmachtdas.de – generates /public from _src.
Run:  python3 _src/build.py
"""
import json, os, re, shutil, html, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_src")
OUT = os.path.join(ROOT, "public")
ICONS = os.path.join(SRC, "icons")
SITE = "https://dasmachtdas.de"
TODAY = "2026-10-13"
import hashlib
VER = hashlib.md5(b"".join(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", d, f), "rb").read() for d, f in (("css", "site.css"), ("js", "site.js")))).hexdigest()[:8]

E = html.escape
TEL = "tel:01792033399"
TEL_TXT = "0179 20 333 99"
WA = "https://wa.me/491721009922"
WA_NAV = "https://wa.me/491792033399"
MAIL = "mailto:info@dasmachtdas.de"
MAPS = "https://maps.google.com/maps?q=DAS%20GmbH%2C%20Heimsheimer%20Str.%2029%2C%2070499%20Stuttgart&z=16&hl=de&output=embed"
ENDPOINT = "https://readdy.ai/api/form/d9vecbeth95mubjtu710"


def icon(name, cls="i"):
    p = os.path.join(ICONS, name + ".svg")
    svg = open(p, encoding="utf-8").read()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{inner}</svg>'


def img(name, alt, w, h, sizes="100vw", lazy=True, cls="", has800=True, fetch=""):
    src = f"/assets/img/{name}.webp"
    srcset = f' srcset="/assets/img/{name}-800.webp 800w, {src} {w}w" sizes="{sizes}"' if has800 else ""
    load = ' loading="lazy" decoding="async"' if lazy else ' decoding="async"'
    c = f' class="{cls}"' if cls else ""
    f = f' fetchpriority="{fetch}"' if fetch else ""
    return f'<img src="{src}"{srcset} alt="{E(alt)}" width="{w}" height="{h}"{load}{f}{c}>'


LOGO = '<img src="/assets/img/{file}.webp" alt="{alt}" width="800" height="214"{extra}>'


def logo(alt="D A S Logo", extra=' loading="lazy" decoding="async"', variant="das-logo"):
    return LOGO.format(file=variant, alt=E(alt), extra=extra)


def btn(href, text, ic, cls="btn--red", ext=False, extra=""):
    t = ' target="_blank" rel="noopener noreferrer"' if ext else ""
    return f'<a class="btn {cls}" href="{href}"{t}{extra}><span>{text}</span><span class="btn__ic">{icon(ic)}</span></a>'


# ---------------------------------------------------------------- content
NAV = [("Leistungen", "#leistungen"), ("Über uns", "#ueber-uns"), ("Services", "#interaktiv"),
       ("Fragen", "#fragen"), ("Gutachten", "#gutachten"), ("Kontakt", "#kontakt")]

SERVICES = [
    ("gutachten", "Gutachten & Bewertung", "gutachten-bewertung", 1600, 900,
     ["Unfallgutachten", "Kaskogutachten", "Beweissicherungsgutachten", "Fahrzeugbewertungen", "Oldtimerbewertungen", "Reparaturbestätigungen", "Reparaturwegprüfungen", "Nachbesichtigungen"]),
    ("technik", "Technik", "technik", 1600, 900,
     ["Achsvermessung", "Rahmenvermessung", "Fahrwerksprüfung", "Fahrzeugdiagnose", "Fehlerspeicher auslesen", "Batterieprüfung", "Bremsenprüfung", "Stoßdämpferprüfung", "Lichttest", "Klimaservice"]),
    ("werkstatt", "Werkstatt", "werkstatt", 1216, 832,
     ["Wartung und Inspektion", "Ölservice", "Bremsenservice", "Fahrzeugaufbereitung", "Innenraumreinigung", "Lederpflege", "Ozonbehandlung", "Leasingrückgabe-Aufbereitung"]),
    ("instandsetzungen", "Instandsetzungen", "instandsetzungen", 1600, 900,
     ["Unfallinstandsetzung", "Karosseriearbeiten", "Smart Repair", "Scheibenservice", "Lackierung", "Ausbeulen ohne Lackieren", "Kotflügelreparatur", "Stoßstangenreparatur"]),
    ("radwechsel", "Radwechsel", "radwechsel", 600, 400,
     ["Reifenservice", "Räderwechsel", "Reifenmontage", "Reifenwuchten", "Reifenhandel", "Felgenhandel", "Winterreifen-Check", "Sommerreifen-Check"]),
    ("service", "Service", "service", 1448, 1086,
     ["Werkstattservice", "Flottenservice", "Fuhrparkbetreuung", "Fahrzeugchecks", "Urlaubscheck", "Wintercheck", "Sommercheck", "Leasingrückgabe-Check"]),
]

ALSO = [
    ("batterie-wechsel", "Batterie Wechsel", "Schnell & zuverlässig",
     "Wir prüfen Ihre Starterbatterie auf Ladezustand und Leistungsfähigkeit und ersetzen sie bei Bedarf direkt vor Ort – ohne lange Wartezeiten, mit hochwertigen Markenbatterien."),
    ("achsvermessung", "Achsvermessung", "Präzise Fahrwerksjustierung",
     "Mit modernster Laser-Messtechnik stellen wir die Spur Ihrer Räder millimetergenau ein – für optimalen Geradeauslauf, weniger Reifenverschleiß und maximale Fahrsicherheit."),
    ("kuehlmittel", "Kühlmittel nachfüllen", "Damit Ihr Motor kühl bleibt",
     "Wir prüfen den Frostschutz, kontrollieren den Kühlmittelstand und füllen bei Bedarf fachgerecht mit dem passenden Kühlmittel nach – für optimalen Motorschutz zu jeder Jahreszeit."),
]

IA = [
    ("motor", "Motor", "Motor & Diagnose", "Modernste Fahrzeugdiagnose mit Fehlerspeicher-Auslesung, Motoranalyse und umfassender technischer Prüfung. Wir finden jedes Problem – schnell und präzise.", "settings-3-line", 73, 54),
    ("innenraum", "Innenraum", "Innenraum & Aufbereitung", "Professionelle Fahrzeugaufbereitung innen und außen, Lederpflege, Ozonbehandlung und Leasingrückgabe-Aufbereitung. Ihr Auto glänzt wie am ersten Tag.", "sparkling-line", 51, 59),
    ("fahrwerk", "Fahrwerk", "Fahrwerk & Achsvermessung", "Präzise Achs- und Rahmenvermessung mit modernster Lasertechnik. Fahrwerksprüfung und Stoßdämpferdiagnose für maximale Sicherheit und Fahrkomfort.", "steering-line", 27, 64),
    ("bremsen", "Bremsen", "Bremsen & Sicherheit", "Kompletter Bremsenservice: Prüfung, Wartung und Austausch von Bremsbelägen, -scheiben und -flüssigkeit. Ihre Sicherheit hat für uns höchste Priorität.", "alert-line", 82, 62),
    ("reifen", "Reifen", "Reifen & Räder", "Reifenservice, Räderwechsel, Reifenmontage und -wuchten sowie Reifenhandel. Wir sorgen für optimalen Grip zu jeder Jahreszeit.", "contrast-drop-line", 18, 62),
]

FAQ = [
    ("Bekomme ich kurzfristig einen Termin?", "Ja, in vielen Fällen sogar noch am selben Tag. Rufen Sie uns einfach unter 0179 20 333 99 an oder schreiben Sie uns per WhatsApp."),
    ("Ich hatte einen Unfall – was soll ich jetzt tun?", "Rufen Sie uns an, wir sind 24 Stunden erreichbar. Sie erhalten eine kostenlose Ersteinschätzung am Telefon. Danach kümmern wir uns um Kostenvoranschlag, Gutachter-Vermittlung und die Reparatur – alles aus einer Hand."),
    ("Wer bezahlt das Gutachten nach einem Unfall?", "Wenn Sie unverschuldet in einen Unfall geraten sind, trägt in der Regel die gegnerische Haftpflichtversicherung die Kosten für das Gutachten. Bei sehr kleinen Schäden reicht oft ein Kostenvoranschlag – wir beraten Sie gern, was in Ihrem Fall sinnvoll ist."),
    ("Erstellen Sie selbst Gutachten?", "Den Kostenvoranschlag erstellen wir direkt in unserer Meisterwerkstatt. Für ein offizielles Gutachten vermitteln wir Sie an einen unabhängigen, VfK-zertifizierten Kfz-Sachverständigen aus dem Großraum Stuttgart."),
    ("Was kostet ein Kostenvoranschlag und wie schnell bekomme ich ihn?", "Der Kostenvoranschlag ist kostenfrei und unverbindlich. In der Regel erhalten Sie ihn innerhalb von 24 Stunden – mit jeder Position transparent aufgeschlüsselt."),
    ("Verliere ich meine Herstellergarantie, wenn ich zu einer freien Werkstatt gehe?", "Nein. Wartung und Inspektion dürfen auch in einer freien Werkstatt durchgeführt werden, solange nach Herstellervorgaben und mit Teilen in Erstausrüsterqualität gearbeitet wird. Genau so arbeiten wir."),
    ("Kann ich HU und AU bei Ihnen machen lassen?", "Ja. Die Hauptuntersuchung und Abgasuntersuchung wird direkt bei uns im Haus durchgeführt. Kleinere Mängel können wir auf Wunsch gleich vor Ort beheben."),
    ("Welche Leistungen bieten Sie rund um Reifen an?", "Wir übernehmen Räderwechsel, Reifenmontage und Auswuchten und verkaufen Reifen und Felgen. Auf Wunsch prüfen wir dabei auch gleich die Achsvermessung."),
    ("Betreuen Sie auch Firmenfahrzeuge und Flotten?", "Ja. Mit unserem Flottenservice und der Fuhrparkbetreuung kümmern wir uns um Wartung, Reparaturen und Fahrzeugchecks Ihrer Firmenfahrzeuge – planbar und mit festem Ansprechpartner."),
    ("Wo finde ich Sie?", "Sie finden uns in der Heimsheimer Straße 29, 70499 Stuttgart-Weilimdorf. Wir betreuen Kundinnen und Kunden aus Stuttgart und der ganzen Region, zum Beispiel aus Ditzingen, Gerlingen, Korntal-Münchingen, Leonberg und Ludwigsburg."),
]

KV = [
    ("file-list-3-line", "Detaillierte Aufstellung", "Jede Position transparent aufgeschlüsselt – Sie sehen genau, was gemacht wird und was es kostet."),
    ("timer-flash-line", "Schnell & unverbindlich", "In der Regel erhalten Sie Ihren Kostenvoranschlag innerhalb von 24 Stunden – völlig kostenfrei und unverbindlich."),
    ("tools-line", "Direkt aus unserer Meisterwerkstatt", "Erstellt von erfahrenen KFZ-Meistern, die Ihr Fahrzeug kennen – keine Pauschalpreise, sondern faire Kalkulation."),
    ("shield-check-line", "Basis für Versicherung & Bank", "Ideal als Grundlage für die Schadenregulierung oder zur Finanzierungsanfrage bei Ihrer Bank."),
]
GV = [
    ("user-star-line", "Geprüfte Partner-Gutachter", "Wir vermitteln ausschließlich VfK-zertifizierte KFZ-Sachverständige aus der Region – unabhängig und neutral."),
    ("timer-flash-line", "Schnell bei Ihnen vor Ort", "Auf Wunsch vermitteln wir einen Gutachter, der innerhalb einer Stunde bei Ihnen ist – im gesamten Großraum Stuttgart."),
    ("bank-card-line", "Kostenübernahme im Schadensfall", "Im Haftpflichtfall trägt die gegnerische Versicherung die Gutachterkosten – für Sie entstehen keine Kosten."),
    ("shake-hands-line", "Persönliche Empfehlung", "Wir kennen unsere Partner persönlich und empfehlen nur Gutachter, mit denen wir selbst gerne zusammenarbeiten."),
]
AREAS = ["Stuttgart-Mitte", "Stuttgart-Nord", "Stuttgart-Süd", "Stuttgart-Ost", "Stuttgart-West", "Bad Cannstatt", "Feuerbach", "Vaihingen", "Ludwigsburg", "Esslingen", "Böblingen", "Sindelfingen", "Leonberg", "Korntal", "Filderstadt", "Leinfelden-Echterdingen", "Fellbach", "Waiblingen", "Kornwestheim", "Marbach"]

PARTNERS = [
    ("SVK Partner", "https://www.vfk-ev.de", "/assets/img/partner/svk-partner.webp"),
    ("ERGO Versicherung", "https://danijel-aljic.ergo.de", "/assets/img/partner/ergo-versicherung.svg"),
    ("ReSmart Group", "https://resmart-group.de", "/assets/img/partner/resmart-group.webp"),
    ("SBW GmbH", "https://sbwgmbh.de/partner-der-sbw/", "/assets/img/partner/sbw-gmbh.webp"),
    ("V-A-O", "https://v-a-o.de/kosten/", "/assets/img/partner/v-a-o.webp"),
    ("SV Rot 1945", "https://www.sv-rot-1945.de", "/assets/img/partner/sv-rot-1945.webp"),
    ("STD Textildruck", "https://textildruck-1a.com/", "/assets/img/partner/std-textildruck.webp"),
    ("Tamam Design", "https://www.tamamdesign.de/", None),
    ("Fix Reguliert", None, None),
    ("AH Geiger", "https://www.ah-geiger.de/", "/assets/img/partner/ah-geiger.webp"),
    ("Rechtsanwaltskanzlei Esslingen", "https://www.rechtsanwaltskanzlei-esslingen.de/", "/assets/img/partner/rechtsanwaltskanzlei-esslingen.webp"),
    ("Steuerberater Louis", "https://www.steuerberater-louis.de/", "/assets/img/partner/steuerberater-louis.webp"),
    ("Wipersoft", "https://wipersoft.de/", "/assets/img/partner/wipersoft.webp"),
    ("RH Anwaltskanzlei", "https://www.rh-anwaltskanzlei.de/", "/assets/img/partner/rh-anwaltskanzlei.webp"),
    ("Emox Elektro", "https://emox-elektro.de/", "/assets/img/partner/emox-elektro.webp"),
    ("RVR", "https://www.rvr.de/", "/assets/img/partner/rvr.svg"),
    ("Kanzlei PHP", "https://www.kanzlei-php.de", "/assets/img/partner/kanzlei-php.svg"),
    ("DTE Dellentechnik", "https://dte-dellentechnik.de/", "/assets/img/partner/dte-dellentechnik.webp"),
    ("Page Kraft", "https://page-kraft.de", "/assets/img/partner/page-kraft.webp"),
    ("Life Heroes", "https://www.life-heroes.de/", "/assets/img/partner/life-heroes.webp"),
    ("Classic Analytics", "https://www.classic-analytics.de/de", "/assets/img/partner-classic-analytics.webp"),
    ("SV Timmerman", "https://sv-timmerman.de", "/assets/img/partner-sv-timmerman.webp"),
]

JOBS = [
    ("werkstatt-mitarbeiter", "KFZ-Mechatroniker / Werkstatt-Mitarbeiter", "Vollzeit", ["FULL_TIME"], "tools-line",
     "Werden Sie Teil unseres erfahrenen Teams und arbeiten Sie an modernsten Fahrzeugen. Von der Diagnose bis zur Reparatur – Sie übernehmen vielfältige Aufgaben in einer professionellen Meisterwerkstatt.",
     ["Wartung, Inspektion und Reparatur von Fahrzeugen aller Marken", "Durchführung von Fehlerdiagnosen und Auslesen des Fehlerspeichers", "Bremsen-, Achs- und Fahrwerksarbeiten", "Kundenservice und fachliche Beratung", "Dokumentation aller Arbeiten nach Herstellervorgaben"],
     ["Abgeschlossene Ausbildung als KFZ-Mechatroniker (m/w/d)", "Erfahrung in der Fahrzeugdiagnose und -reparatur", "Zuverlässigkeit, Teamfähigkeit und Eigeninitiative", "Deutsche Sprache in Wort und Schrift", "Führerschein Klasse B"]),
    ("reifen-helfer", "Helfer Reifenwechsel & Reifenmontage", "Vollzeit / Teilzeit", ["FULL_TIME", "PART_TIME"], "contrast-drop-line",
     "Unterstützen Sie unser Team bei der schnellen und professionellen Reifenumrüstung. Sie arbeiten mit modernen Maschinen und sorgen dafür, dass unsere Kunden sicher und pünktlich unterwegs sind.",
     ["Professionelles Reifenmontieren und Reifenwuchten", "Saisonaler Räderwechsel für Pkw und SUVs", "Überprüfung des Luftdrucks und Zustands der Reifen", "Lagerung und Bestandsmanagement der Kundenreifen", "Unterstützung bei der Kundenbetreuung"],
     ["Handwerkliches Geschick und technisches Verständnis", "Erfahrung im Reifenservice wünschenswert (kein Muss)", "Zuverlässigkeit und sorgfältige Arbeitsweise", "Körperliche Belastbarkeit und Teamgeist", "Deutsche Sprache in Wort und Schrift"]),
    ("werkstatt-manager", "Werkstattleiter / Service-Manager", "Vollzeit", ["FULL_TIME"], "user-settings-line",
     "Führen Sie unsere Werkstatt mit Weitsicht und Hands-on-Mentalität. Sie koordinieren das Tagesgeschäft, leiten das Team und sorgen dafür, dass Qualität, Effizienz und Kundenzufriedenheit stets auf höchstem Niveau bleiben.",
     ["Leitung und Koordination des gesamten Werkstattteams", "Terminplanung und Ressourcenmanagement", "Qualitätskontrolle und Einhaltung von Herstellervorgaben", "Kundenberatung bei komplexen technischen Fragen", "Zusammenarbeit mit Versicherungen und Gutachtern", "Weiterentwicklung von Abläufen und Standards"],
     ["Meisterqualifikation oder Techniker im KFZ-Bereich", "Mehrjährige Führungserfahrung in einer Werkstatt", "Hervorragende Organisations- und Kommunikationsfähigkeiten", "Kundenorientierte Denkweise und Lösungskompetenz", "Deutsche Sprache fließend in Wort und Schrift"]),
]
BENEFITS = [
    ("money-euro-circle-line", "Attraktive Vergütung", "Leistungsgerechte Bezahlung mit Entwicklungsperspektive"),
    ("time-line", "Flexible Arbeitszeiten", "Faire Schichtmodelle und Work-Life-Balance"),
    ("tools-line", "Moderne Ausstattung", "Neueste Diagnosegeräte und Werkstatttechnik"),
    ("graduation-cap-line", "Weiterbildung", "Regelmäßige Schulungen und Zertifizierungen"),
    ("team-line", "Tolles Team", "Offene Unternehmenskultur und kurze Wege"),
    ("medal-line", "Meisterwerkstatt", "Hohe Qualitätsstandards und beste Reputation"),
    ("car-line", "Firmenwagen", "Ersatzfahrzeug bei Reparatur Ihres Privatwagens"),
    ("gift-line", "Mitarbeiterrabatte", "Vergünstigungen auf alle Werkstattleistungen"),
]

# ---------------------------------------------------------------- structured data
BIZ_ID = SITE + "/#business"
WEB_ID = SITE + "/#website"


def business():
    catalog = {"@type": "OfferCatalog", "name": "Leistungen", "itemListElement": [
        {"@type": "OfferCatalog", "name": s[1], "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": it}} for it in s[5]]}
        for s in SERVICES]}
    return {
        "@type": "AutoRepair", "@id": BIZ_ID, "name": "DAS GmbH",
        "description": "Professionelle Kfz-Werkstatt in Stuttgart. Wartung, Reparatur, Gutachten, Fahrzeugservice, Reifenwechsel & mehr.",
        "url": SITE + "/",
        "logo": {"@type": "ImageObject", "url": SITE + "/assets/img/das-logo.png", "width": 1276, "height": 342},
        "image": [SITE + "/og-image.jpg", SITE + "/assets/img/standort-banner.webp"],
        "telephone": "+491792033399", "email": "info@dasmachtdas.de",
        "address": {"@type": "PostalAddress", "streetAddress": "Heimsheimer Straße 29", "postalCode": "70499",
                    "addressLocality": "Stuttgart", "addressRegion": "Baden-Württemberg", "addressCountry": "DE"},
        "geo": {"@type": "GeoCoordinates", "latitude": 48.820518, "longitude": 9.100159},
        "hasMap": "https://www.google.com/maps/search/?api=1&query=DAS+GmbH+Heimsheimer+Stra%C3%9Fe+29+70499+Stuttgart",
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "08:00", "closes": "17:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "11:00", "closes": "14:00"}],
        "areaServed": [{"@type": "City", "name": n} for n in ["Stuttgart", "Ditzingen", "Gerlingen", "Korntal-Münchingen", "Leonberg", "Ludwigsburg", "Esslingen", "Böblingen", "Sindelfingen", "Fellbach", "Waiblingen", "Kornwestheim"]],
        "hasOfferCatalog": catalog,
        "contactPoint": {"@type": "ContactPoint", "telephone": "+491792033399", "contactType": "customer service", "availableLanguage": "de", "hoursAvailable": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "00:00", "closes": "23:59"}},
    }


def website():
    return {"@type": "WebSite", "@id": WEB_ID, "url": SITE + "/", "name": "DAS GmbH", "inLanguage": "de-DE", "publisher": {"@id": BIZ_ID}}


def webpage(path, name, desc, crumbs):
    url = SITE + path
    page = {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": name, "description": desc,
            "inLanguage": "de-DE", "isPartOf": {"@id": WEB_ID}, "about": {"@id": BIZ_ID},
            "primaryImageOfPage": {"@type": "ImageObject", "url": SITE + "/og-image.jpg"}}
    bc = {"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + p} for i, (n, p) in enumerate(crumbs)]}
    page["breadcrumb"] = {"@id": bc["@id"]}
    return [page, bc]


def ld(graph):
    s = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    return f'<script type="application/ld+json">{s.replace("</", "<\\/")}</script>'


# ---------------------------------------------------------------- shared chrome
def head(path, title, desc, graph, robots="index, follow", preload=""):
    url = SITE + path
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0A0A0A">
<meta name="geo.region" content="DE-BW">
<meta name="geo.placename" content="Stuttgart-Weilimdorf">
<meta name="geo.position" content="48.820518;9.100159">
<meta name="ICBM" content="48.820518, 9.100159">
<meta property="og:type" content="website">
<meta property="og:locale" content="de_DE">
<meta property="og:site_name" content="DAS GmbH">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og-image.jpg">
<meta property="og:image:secure_url" content="{SITE}/og-image.jpg">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="DAS GmbH – Kfz-Werkstatt &amp; Service in Stuttgart">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(desc)}">
<meta name="twitter:image" content="{SITE}/og-image.jpg">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon-32.png" type="image/png" sizes="32x32">
<link rel="icon" href="/icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/archivo-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/jakarta-var.woff2" as="font" type="font/woff2" crossorigin>
{preload}<link rel="stylesheet" href="/assets/css/site.css?v={VER}">
<script src="/assets/js/site.js?v={VER}" defer></script>
{ld(graph)}
</head>
"""


def header(home=True):
    pre = "" if home else "/"
    links = "".join(f'<a href="{pre}{h}">{t}</a>' for t, h in NAV)
    cur = ' aria-current="page"' if not home else ""
    menu_links = "".join(f'<a href="{pre}{h}"><span>{t}</span></a>' for t, h in NAV) + f'<a href="/jobs"{cur}><span>Karriere</span></a>'
    return f"""<a class="skip" href="#main">Zum Inhalt springen</a>
<div id="top-sentinel" aria-hidden="true"></div>
<header class="nav">
  <div class="nav__bar">
    <a class="nav__logo" href="/" aria-label="DAS GmbH – Startseite">{logo(extra=' decoding="async"')}</a>
    <nav class="nav__links" aria-label="Hauptnavigation">{links}<a href="/jobs"{cur}>Karriere</a></nav>
    <div class="nav__cta">
      {btn(WA_NAV, "WhatsApp", "whatsapp-line", "btn--wa", ext=True)}
      {btn(TEL, "Anrufen", "phone-line", "btn--red")}
    </div>
    <div class="nav__right">
      <a class="call-ic" href="{TEL}" aria-label="Anrufen">{icon("phone-line")}</a>
      <button class="burger" type="button" aria-expanded="false" aria-controls="menu" aria-label="Menü öffnen"><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="menu" id="menu" aria-hidden="true" inert>
  <nav class="menu__links" aria-label="Mobile Navigation">{menu_links}</nav>
  <div class="btn-row">
    {btn(WA_NAV, "WhatsApp", "whatsapp-line", "btn--wa", ext=True)}
    {btn(TEL, "Anrufen", "phone-line", "btn--red")}
  </div>
</div>
"""


def footer(home=True):
    pre = "" if home else "/"
    leist = "".join(f'<li><a href="{pre}#leistungen">{t}</a></li>' for t in ["Gutachten", "Werkstatt", "Technik", "Fahrzeugpflege", "Mobilität", "Handel"])
    navl = "".join(f'<li><a href="{pre}{h}">{t}</a></li>' for t, h in NAV)
    return f"""<footer class="footer">
  <div class="wrap">
    <div class="footer__grid">
      <div>
        <a class="logo-free" href="/" aria-label="DAS GmbH – Startseite">{logo(variant="das-logo-light")}</a>
        <p class="footer__about">Ihr kompetenter Partner für Werkstatt, Gutachten und Fahrzeugservice in Stuttgart und Umgebung.</p>
      </div>
      <div><h4>Leistungen</h4><ul>{leist}</ul></div>
      <div><h4>Navigation</h4><ul>{navl}<li><a href="/jobs">Karriere</a></li><li><a href="/impressum">Impressum</a></li><li><a href="/datenschutz">Datenschutz</a></li></ul></div>
      <div><h4>Kontakt</h4>
        <ul class="flist">
          <li>{icon("phone-line")}<a href="{TEL}">{TEL_TXT}</a></li>
          <li>{icon("mail-line")}<a href="{MAIL}">Info@dasmachtdas.de</a></li>
          <li>{icon("whatsapp-line")}<a href="{WA}" target="_blank" rel="noopener noreferrer">WhatsApp</a></li>
          <li>{icon("map-pin-line")}<span>Heimsheimer Straße 29<br>70499 Stuttgart</span></li>
          <li>{icon("time-line")}<span>Montag – Freitag 08:00 – 17:00 Uhr<br>Samstag 11:00 – 14:00 Uhr</span></li>
        </ul>
      </div>
    </div>
    <div class="footer__bar">
      <p>© 2026 DAS GmbH · Heimsheimer Straße 29 · 70499 Stuttgart</p>
      <nav aria-label="Rechtliches"><a href="/impressum">Impressum</a><span aria-hidden="true">|</span><a href="/datenschutz">Datenschutz</a></nav>
    </div>
  </div>
</footer>
"""


# ---------------------------------------------------------------- index sections
def promo_slider():
    return f"""<section class="promo" aria-roledescription="Karussell" aria-label="Aktionen">
  <div class="promo__frame rv" data-slider>
    <div class="slide slide--wrap is-active" aria-roledescription="Folie" aria-label="1 von 2">
      <div class="slide__media">{img("auto-beklebung-g-klasse", "Mercedes G-Klasse mit DAS-Werbebeklebung", 1600, 900)}</div>
      <div class="slide__body">
        <span class="eyebrow eyebrow--red">{icon("car-line")}Auto-Beklebung</span>
        <h2>Lass dein Auto mit unserer Werbung bekleben</h2>
        <p class="slide__kicker">und sichere dir 1 Jahr kostenfreie Autowäsche</p>
        <p class="slide__text">Dein Fahrzeug wird zur rollenden Werbefläche – professionell beklebt und ein ganzes Jahr lang kostenlos gewaschen. Sichere dir jetzt einen der limitierten Plätze.</p>
        <div class="btn-row">
          {btn(TEL, "Jetzt anfragen", "phone-line", "btn--red")}
          {btn("#kontakt", "Mehr erfahren", "mail-send-line", "btn--light")}
        </div>
      </div>
    </div>
    <div class="slide slide--promo" aria-roledescription="Folie" aria-label="2 von 2">
      <div class="slide__media">{img("sonderangebot-paar", "Glückliches Paar mit Tablet", 1600, 533)}</div>
      <div class="slide__body">
        {logo(extra=' class="slide__logo" loading="lazy" decoding="async"')}
        <span class="eyebrow">Sonderangebot</span>
        <h2>40 € RABATT<span>auf Ihren nächsten Service</span></h2>
        <p class="slide__text">Nutzen Sie unser limitiertes Angebot und sparen Sie <strong>40 €</strong> bei Ihrem nächsten Werkstattbesuch. Gültig auf alle Serviceleistungen — melden Sie sich jetzt an!</p>
      </div>
    </div>
    <div class="dots"><button type="button" aria-label="Banner 1" aria-current="true"></button><button type="button" aria-label="Banner 2" aria-current="false"></button></div>
  </div>
</section>
"""


def services():
    cards = []
    for n, (sid, title, im, w, h, items) in enumerate(SERVICES):
        vis, rest = items[:6], items[6:]
        lis = "".join(f'<li>{icon("check-line")}<span>{E(t)}</span></li>' for t in vis)
        extra = ""
        if rest:
            lis += f'<li class="more-count">+{len(rest)} weitere</li>'
            rl = "".join(f'<li>{icon("check-line")}<span>{E(t)}</span></li>' for t in rest)
            extra = f"""<div class="collapse" id="more-{sid}" aria-hidden="true"><div><ul class="checks checks--extra">{rl}</ul></div></div>
          <button class="toggle" type="button" data-more aria-expanded="false" aria-controls="more-{sid}"><span class="toggle__l">Alle anzeigen</span>{icon("arrow-down-s-line")}</button>"""
        sizes = "(max-width: 900px) 100vw, 720px"
        has800 = w > 800
        d = f" rv-d{n % 2}" if n % 2 else ""
        cards.append(f"""<article class="svc bezel rv{d}" id="leistung-{sid}">
        <div class="bezel__core">
          <div class="svc__media">{img(im, title, w, h, sizes, has800=has800)}<div class="svc__title"><h3>{E(title)}</h3><span class="svc__num">0{n+1}</span></div></div>
          <div class="svc__body"><ul class="checks">{lis}</ul>{extra}</div>
        </div>
      </article>""")
    return f"""<section class="section" id="leistungen">
  <div class="wrap">
    <div class="sec-head rv">
      <span class="logo-free">{logo()}</span>
      <h2 class="h-lg">Alles rund ums Auto <span class="red h-sub">– kompetent und aus einer Hand</span></h2>
    </div>
    <div class="bento">
      {"".join(cards)}
    </div>
  </div>
</section>
"""


def also():
    cards = "".join(f"""<article class="bezel rv rv-d{i}">
        <div class="bezel__core">
          <div class="also__media">{img(im, t, 480, 320, has800=False)}<div class="also__cap"><h3>{E(t)}</h3><p>{E(st)}</p></div></div>
          <div class="also__body"><p>{E(dsc)}</p><a class="link-arrow" href="#kontakt">Mehr erfahren {icon("arrow-right-line")}</a></div>
        </div>
      </article>""" for i, (im, t, st, dsc) in enumerate(ALSO))
    return f"""<section class="panel panel--red section" aria-labelledby="also-h">
  <div class="wrap">
    <div class="also-head rv">
      <span class="logo-free">{logo("DAS Logo", variant="das-logo-white")}</span>
      <h2 class="h-lg" id="also-h">machen wir auch</h2>
    </div>
    <div class="also">{cards}</div>
  </div>
</section>
"""


def about():
    return f"""<section class="section about" id="ueber-uns">
  <div class="wrap split">
    <div class="about__media rv">
      <div class="bezel"><div class="bezel__core">{img("standort-banner", "DAS Kfz-Werkstatt Banner am Standort", 1449, 1085, "(max-width: 900px) 100vw, 600px")}</div></div>
      <div class="about__badge">{icon("map-pin-line")}<span>Heimsheimer Straße 29<br>70499 Stuttgart</span></div>
    </div>
    <div class="rv rv-d1">
      <h2 class="h-lg">Ihr vertrauensvoller Partner für <span class="red nowrap">Kfz-Service</span> in Stuttgart</h2>
      <p class="lead">Seit über 20 Jahren steht DAS für erstklassigen Fahrzeugservice mit Leidenschaft und technischer Präzision. Unser erfahrenes Team kombiniert traditionelles Handwerk mit modernster Diagnosetechnik, um jedes Fahrzeug zuverlässig und sicher auf die Straße zu bringen. Dabei ist uns eine ehrliche, transparente Beratung genauso wichtig wie die Qualität unserer Arbeit.</p>
      <div class="btn-row">
        {btn(TEL, "Jetzt anrufen", "phone-line", "btn--red")}
        {btn("#leistungen", "Unsere Leistungen", "arrow-down-line", "btn--light")}
      </div>
    </div>
  </div>
</section>
"""


def interactive():
    data = {i[0]: {"title": i[2], "description": i[3], "x": i[5], "y": i[6]} for i in IA}
    hs = "".join(f'<button class="hs{" is-active" if k == 0 else ""}" type="button" data-id="{i[0]}" aria-label="{i[1]}"><span class="hs__label">{i[1]}</span></button>' for k, i in enumerate(IA))
    chips = "".join(f'<button class="chip" type="button" role="tab" data-id="{i[0]}" aria-selected="{"true" if k == 0 else "false"}" aria-controls="ia-panel" tabindex="{0 if k == 0 else -1}">{i[1]}</button>' for k, i in enumerate(IA))
    tpl = "".join(f'<template id="ic-{i[0]}">{icon(i[4])}</template>' for i in IA)
    first = IA[0]
    return f"""<section class="panel panel--dark section" id="interaktiv" data-ia>
  <div class="wrap">
    <div class="ia-head rv">
      <span class="logo-free ia-logo">{logo(variant="das-logo-light")}</span>
      <h2 class="h-lg">Alles aus einer Hand</h2>
    </div>
    <div class="ia">
      <div class="car bezel bezel--dark rv"><div class="bezel__core">{img("fahrzeugansicht", "Interaktive Fahrzeugansicht", 991, 750, "(max-width: 900px) 100vw, 760px")}{hs}</div></div>
      <div class="ia-side rv rv-d1">
        <div class="ia-card bezel bezel--dark" id="ia-panel" role="tabpanel" aria-live="polite"><div class="bezel__core">
          <div class="ia-card__ic fade">{icon(first[4])}</div>
          <h3 class="ia-t fade">{E(first[2])}</h3>
          <p class="ia-d fade">{E(first[3])}</p>
          <a class="link-arrow" href="#kontakt">Jetzt anfragen {icon("arrow-right-line")}</a>
        </div></div>
        <div class="chips" role="tablist" aria-label="Fahrzeugbereiche">{chips}</div>
      </div>
    </div>
  </div>
  {tpl}
  <script type="application/json" id="ia-data">{json.dumps(data, ensure_ascii=False)}</script>
</section>
"""


def faq():
    items = []
    for k, (q, a) in enumerate(FAQ):
        op = k == 0
        items.append(f"""<div class="qa__item{" is-open" if op else ""} rv" data-acc>
        <h3><button class="qa__btn" type="button" aria-expanded="{"true" if op else "false"}" aria-controls="qa-{k}" id="qa-b{k}"><span>{E(q)}</span><span class="qa__plus">{icon("add-line")}</span></button></h3>
        <div class="collapse qa__a{" is-open" if op else ""}" id="qa-{k}" role="region" aria-labelledby="qa-b{k}" aria-hidden="{"false" if op else "true"}"><div><p>{E(a)}</p></div></div>
      </div>""")
    return f"""<section class="section" id="fragen">
  <div class="wrap faq">
    <div class="faq__intro rv">
      <h2 class="h-lg">Häufige Fragen</h2>
      <p class="lead">Die wichtigsten Antworten rund um Werkstatt, Unfall und Gutachten – kurz und ehrlich.</p>
      {btn(TEL, "Frage nicht dabei? Jetzt anrufen", "phone-line", "btn--red")}
    </div>
    <div class="qa">{"".join(items)}</div>
  </div>
</section>
"""


def gutachten():
    def feats(lst):
        return "".join(f'<li><span class="feat__ic">{icon(ic)}</span><h4>{E(t)}</h4><p>{E(dsc)}</p></li>' for ic, t, dsc in lst)
    areas = "".join(f"<li>{E(a)}</li>" for a in AREAS)
    return f"""<section class="section" id="gutachten">
  <div class="wrap">
    <div class="ga-title rv">
      <span class="logo-free">{logo()}</span>
      <h2 class="h-lg">Kostenvoranschlag? Vermittlung an einen unabhängigen Gutachter? <span class="inline-logo red">{logo("DAS")}kann beides!</span></h2>
    </div>
    <div class="ga">
      <article class="bezel ga--light rv"><div class="bezel__core">
        <span class="ga__tag">{icon("tools-line")}Direkt von uns</span>
        <h3>Professioneller Kostenvoranschlag</h3>
        <p class="lead">Sie benötigen eine detaillierte Kostenaufstellung für eine Reparatur oder Wartung? Unser Meister-Team erstellt Ihnen einen transparenten, fairen Kostenvoranschlag – schnell, unverbindlich und direkt aus unserer Werkstatt.</p>
        <ul class="feat">{feats(KV)}</ul>
        {btn("#kontakt", "Kostenvoranschlag anfordern", "mail-line", "btn--red")}
      </div></article>
      <article class="bezel ga--dark rv rv-d1"><div class="bezel__core">
        <span class="ga__tag ga__tag--dark">{icon("user-star-line")}Partner-Vermittlung</span>
        <h3>Unabhängiger Gutachter aus der Region</h3>
        <p class="lead">Sie brauchen ein offizielles Gutachten? Wir vermitteln Sie an einen unserer geprüften, unabhängigen Partner-Gutachter aus dem Großraum Stuttgart – VfK-zertifiziert, neutral und schnell bei Ihnen vor Ort.</p>
        <ul class="feat">{feats(GV)}</ul>
        <div class="area"><p class="area__h">{icon("map-pin-range-line")}Einsatzgebiet der Partner</p><ul>{areas}</ul></div>
        {btn(TEL, "Jetzt anrufen: 0179 20 333 99", "phone-line", "btn--light")}
      </div></article>
    </div>
  </div>
</section>
"""


def kontakt():
    return f"""<section class="section" id="kontakt">
  <div class="wrap">
    <div class="sec-head rv">
      <h2 class="h-lg">Kontakt</h2>
      <p class="lead">Ob Gutachten, Werkstatt oder Service – wir sind für Sie da. Rufen Sie an oder schreiben Sie uns.</p>
    </div>
    <div class="contact">
      <div class="contact__left">
        <div class="map bezel rv"><div class="bezel__core">
          <div class="map__ph">
            <span class="map__pin">{icon("map-pin-line")}</span>
            <p class="map__addr">Heimsheimer Straße 29, 70499 Stuttgart</p>
            <button class="btn btn--light btn--sm" type="button" data-map="{MAPS}"><span>Karte laden</span><span class="btn__ic">{icon("map-pin-line")}</span></button>
            <p>Beim Laden der Karte werden Daten an Google übertragen.</p>
          </div>
        </div></div>
        <div class="cgrid rv rv-d1">
          <a class="ccard" href="{TEL}"><span class="ccard__ic">{icon("phone-line")}</span><div><p class="ccard__k">24 h Service-Hotline</p><p class="ccard__v">{TEL_TXT}</p></div></a>
          <a class="ccard" href="{MAIL}"><span class="ccard__ic">{icon("mail-line")}</span><div><p class="ccard__k">E-Mail</p><p class="ccard__v">Info@dasmachtdas.de</p></div></a>
          <a class="ccard" href="{WA}" target="_blank" rel="noopener noreferrer"><span class="ccard__ic">{icon("whatsapp-line")}</span><div><p class="ccard__k">WhatsApp</p><p class="ccard__v">Nachricht senden</p></div></a>
          <div class="ccard"><span class="ccard__ic ccard__ic--n">{icon("map-pin-line")}</span><div><p class="ccard__k">Büro</p><p class="ccard__v">Heimsheimer Straße 29<br>70499 Stuttgart</p></div></div>
          <div class="ccard ccard--wide"><span class="ccard__ic">{icon("time-line")}</span><div><p class="ccard__k">Öffnungszeiten</p><div class="hours"><div><span>Montag – Freitag</span><span>08:00 – 17:00 Uhr</span></div><div><span>Samstag</span><span>11:00 – 14:00 Uhr</span></div></div></div></div>
        </div>
      </div>
      <div class="sos rv rv-d2">
        <span class="sos__ic">{icon("phone-line")}</span>
        <h3>Unfall gehabt? Wir sind sofort für Sie da.</h3>
        <p>Kostenlose Ersteinschätzung am Telefon – im Haftpflichtfall zahlt die gegnerische Versicherung Ihr Gutachten.</p>
        {btn(TEL, TEL_TXT, "phone-line", "btn--white")}
        <span class="live">24 h erreichbar</span>
      </div>
    </div>
  </div>
</section>
"""


def partners():
    tiles = []
    for name, url, src in PARTNERS:
        sq = ' class="sq"' if src and any(k in src for k in ("sv-rot", "v-a-o", "sbw-gmbh", "emox", "sv-timmerman", "std-textildruck")) else ""
        if src and "esslingen" in src: sq = ' class="wide"'
        im = f'<img src="{src}" alt="{E(name)}"{sq} loading="lazy" decoding="async">' if src else f'<span class="partner__name">{E(name)}</span>'
        if url:
            tiles.append(f'<a class="partner" href="{url}" target="_blank" rel="noopener noreferrer" title="{E(name)}">{im}</a>')
        else:
            tiles.append(f'<div class="partner" title="{E(name)}">{im}</div>')
    return f"""<section class="section" aria-labelledby="partner-h">
  <div class="wrap">
    <div class="sec-head rv">
      <span class="eyebrow">Netzwerk &amp; Kooperationen</span>
      <h2 class="h-lg" id="partner-h">Unsere Partner</h2>
      <p class="lead">Wir arbeiten mit einem starken Netzwerk aus Anwälten, Werkstätten und Dienstleistern zusammen — für Ihre vollständige Schadensabwicklung aus einer Hand.</p>
    </div>
    <div class="partners rv">{"".join(tiles)}</div>
  </div>
</section>
"""


def hero():
    return f"""<section class="hero">
  <div class="hero__frame">
    <div class="hero__img">{img("hero-kfz-meister", "DAS GmbH - Kfz-Meister in Stuttgart", 1600, 900, lazy=False, fetch="high")}</div>
    <div class="hero__content">
      <div class="hero__tags">
        <span class="eyebrow eyebrow--dark">{icon("shield-check-line")}Ihr Partner für alles rund ums Auto</span>
        <span class="eyebrow eyebrow--dark">{icon("map-pin-line")}Stuttgart</span>
      </div>
      <h1 class="h-xl">KFZ Werkstatt in Stuttgart</h1>
      <div class="hero__rule" aria-hidden="true"></div>
      <p class="hero__sub">Von Achsvermessung bis Aufbereitung – alles aus einer Hand. Schnell, fair, erfahren.</p>
      <div class="btn-row">
        {btn(TEL, "Termin vereinbaren", "phone-line", "btn--red")}
        {btn(WA, "Per WhatsApp", "whatsapp-line", "btn--glass", ext=True)}
      </div>
      <ul class="hero__trust">
        <li class="trust"><span class="trust__ic">{icon("calendar-check-line")}</span>Termin auch am selben Tag</li>
        <li class="trust"><span class="trust__ic">{icon("scales-3-line")}</span>Unabhängig &amp; fair</li>
        <li class="trust"><span class="trust__ic">{icon("tools-line")}</span>Alles aus einer Hand</li>
      </ul>
    </div>
  </div>
</section>
"""


INDEX_TITLE = "DAS GmbH – Kfz-Werkstatt & Service in Stuttgart"
INDEX_DESC = "Professionelle Kfz-Werkstatt in Stuttgart. Wartung, Reparatur, Gutachten, Fahrzeugservice, Reifenwechsel & mehr. Jetzt Termin vereinbaren."


def page_index():
    faqld = {"@type": "FAQPage", "@id": SITE + "/#faq", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    graph = [business(), website()] + webpage("/", INDEX_TITLE, INDEX_DESC, [("Startseite", "/")]) + [faqld]
    preload = '<link rel="preload" as="image" href="/assets/img/hero-kfz-meister.webp" imagesrcset="/assets/img/hero-kfz-meister-800.webp 800w, /assets/img/hero-kfz-meister.webp 1600w" imagesizes="100vw" fetchpriority="high">\n'
    body = (header(True) + '<main id="main">' + hero() + promo_slider() + services() + also() + about()
            + interactive() + faq() + gutachten() + kontakt() + partners() + "</main>" + footer(True))
    return head("/", INDEX_TITLE, INDEX_DESC, graph, preload=preload) + "<body>\n" + body + "</body>\n</html>\n"


JOBS_TITLE = "Karriere – Jobs bei der DAS GmbH Kfz-Werkstatt in Stuttgart"
JOBS_DESC = "Wir suchen engagierte Fachkräfte, die mit Leidenschaft an modernen Fahrzeugen arbeiten und echte Lösungen für echte Menschen schaffen."


def page_jobs():
    postings = []
    for jid, title, typ, emp, ic, dsc, tasks, reqs in JOBS:
        hd = (f"<p>{E(dsc)}</p><h3>Ihre Aufgaben</h3><ul>" + "".join(f"<li>{E(t)}</li>" for t in tasks)
              + "</ul><h3>Was Sie mitbringen</h3><ul>" + "".join(f"<li>{E(t)}</li>" for t in reqs) + "</ul>")
        postings.append({"@type": "JobPosting", "@id": f"{SITE}/jobs#{jid}", "title": title, "description": hd,
                         "datePosted": TODAY, "employmentType": emp if len(emp) > 1 else emp[0],
                         "hiringOrganization": {"@type": "Organization", "name": "DAS GmbH", "sameAs": SITE + "/", "logo": SITE + "/assets/img/das-logo.png"},
                         "jobLocation": {"@type": "Place", "address": {"@type": "PostalAddress", "streetAddress": "Heimsheimer Straße 29", "postalCode": "70499", "addressLocality": "Stuttgart", "addressRegion": "Baden-Württemberg", "addressCountry": "DE"}},
                         "directApply": True, "url": f"{SITE}/jobs"})
    graph = [business(), website()] + webpage("/jobs", JOBS_TITLE, JOBS_DESC, [("Startseite", "/"), ("Karriere", "/jobs")]) + postings

    cards = []
    for jid, title, typ, emp, ic, dsc, tasks, reqs in JOBS:
        tl = "".join(f'<li>{icon("check-line")}<span>{E(t)}</span></li>' for t in tasks)
        rl = "".join(f'<li>{icon("check-line")}<span>{E(t)}</span></li>' for t in reqs)
        cards.append(f"""<article class="job bezel rv" id="{jid}" data-acc><div class="bezel__core">
        <button class="job__btn" type="button" aria-expanded="false" aria-controls="job-{jid}">
          <span class="job__ic">{icon(ic)}</span>
          <span><span class="job__meta"><span>{E(typ)}</span><span>{icon("map-pin-line")}Stuttgart</span></span><h3>{E(title)}</h3></span>
          <span class="job__chev">{icon("arrow-down-s-line")}</span>
        </button>
        <div class="collapse" id="job-{jid}" aria-hidden="true"><div><div class="job__body">
          <p>{E(dsc)}</p>
          <div class="job__cols">
            <div class="job__col"><h4>{icon("list-check-3")}Ihre Aufgaben</h4><ul class="checks">{tl}</ul></div>
            <div class="job__col"><h4>{icon("user-star-line")}Was Sie mitbringen</h4><ul class="checks">{rl}</ul></div>
          </div>
          {btn("#bewerbung", "Jetzt bewerben", "send-plane-line", "btn--red")}
        </div></div></div>
      </div></article>""")
    ben = "".join(f'<div class="benefit bezel rv"><div class="bezel__core"><span class="benefit__ic">{icon(ic)}</span><h3>{E(t)}</h3><p>{E(dsc)}</p></div></div>' for ic, t, dsc in BENEFITS)
    opts = "".join(f'<option value="{jid}">{E(t)}</option>' for jid, t, *_ in JOBS)
    body = header(False) + f"""<main id="main">
<section class="jhero"><div class="jhero__frame">
  <span class="logo-free">{logo(extra=' decoding="async"', variant="das-logo-light")}</span>
  <h1 class="h-xl">Werden Sie Teil des Teams</h1>
  <p class="lead">Wir suchen engagierte Fachkräfte, die mit Leidenschaft an modernen Fahrzeugen arbeiten und echte Lösungen für echte Menschen schaffen.</p>
</div></section>
<section class="section"><div class="wrap">
  <div class="sec-head rv"><h2 class="h-lg">Offene Stellen</h2><p class="lead">Finden Sie Ihren Platz in unserem wachsenden Team</p></div>
  <div class="jobs">{"".join(cards)}</div>
</div></section>
<section class="section" style-none><div class="wrap">
  <div class="sec-head rv"><h2 class="h-lg">Das erwartet Sie bei uns</h2><p class="lead">Mehr als nur ein Job – ein Team, das zusammenhält</p></div>
  <div class="benefits">{ben}</div>
</div></section>
<section class="section" id="bewerbung"><div class="wrap apply">
  <div class="sec-head rv"><span class="eyebrow">Bewerbung</span><h2 class="h-lg">Bewerben Sie sich jetzt</h2><p class="lead">Teilen Sie uns mit, auf welche Stelle Sie sich bewerben möchten – wir melden uns umgehend bei Ihnen.</p></div>
  <div class="form bezel rv"><div class="bezel__core">
    <form method="POST" action="{ENDPOINT}" data-endpoint="{ENDPOINT}" data-readdy-form="bewerbung" novalidate-none>
      <input class="hp" type="text" name="website_alt" tabindex="-1" autocomplete="off" aria-hidden="true">
      <div class="frow">
        <div class="field"><label for="vorname">Vorname *</label><input type="text" id="vorname" name="vorname" required placeholder="Max" autocomplete="given-name"></div>
        <div class="field"><label for="nachname">Nachname *</label><input type="text" id="nachname" name="nachname" required placeholder="Mustermann" autocomplete="family-name"></div>
      </div>
      <div class="frow">
        <div class="field"><label for="email">E-Mail *</label><input type="email" id="email" name="email" required placeholder="max@beispiel.de" autocomplete="email"></div>
        <div class="field"><label for="telefon">Telefon</label><input type="tel" id="telefon" name="telefon" placeholder="0179 20 333 99" autocomplete="tel"></div>
      </div>
      <div class="field"><label for="stelle">Gewünschte Stelle *</label><select id="stelle" name="stelle" required><option value="">Bitte wählen</option>{opts}</select></div>
      <div class="field"><label for="nachricht">Nachricht / Motivationsschreiben (max. 500 Zeichen)</label><textarea id="nachricht" name="nachricht" rows="5" maxlength="500" placeholder="Warum möchten Sie Teil unseres Teams werden?" aria-describedby="nachricht-h"></textarea><p class="hint" id="nachricht-h">Maximal 500 Zeichen</p></div>
      <div class="msg msg--ok" role="status">{icon("checkbox-circle-line")}<span>Vielen Dank für Ihre Bewerbung! Wir melden uns umgehend bei Ihnen.</span></div>
      <div class="msg msg--err" role="alert">{icon("error-warning-line")}<span class="msg__t"></span></div>
      <button class="btn btn--red" type="submit"><span>Bewerbung absenden</span><span class="btn__ic">{icon("send-plane-line")}</span></button>
    </form>
  </div></div>
  <p class="apply__alt">Oder bewerben Sie sich direkt per E-Mail an <a href="{MAIL}">info@dasmachtdas.de</a></p>
</div></section>
</main>
""" + footer(False)
    return head("/jobs", JOBS_TITLE, JOBS_DESC, graph) + "<body>\n" + body + "</body>\n</html>\n"


def legal_page(path, title, h1, crumb, inner, other):
    desc = f"{h1} der DAS GmbH, Heimsheimer Straße 29, 70499 Stuttgart."
    graph = [business(), website()] + webpage(path, title, desc, [("Startseite", "/"), (crumb, path)])
    body = f"""<header class="lhead"><div class="lhead__bar">
  <a href="/" aria-label="DAS GmbH – Startseite">{logo(extra=' decoding="async"')}</a>
  <a class="btn btn--light btn--sm" href="/"><span>← Zurück zur Startseite</span></a>
</div></header>
<main id="main" class="legal">
  <h1 class="h-lg">{h1}</h1>
  <div class="bezel"><div class="bezel__core">{inner}</div></div>
</main>
<footer class="lfoot"><p>© 2026 DAS GmbH</p><nav aria-label="Rechtliches"><a href="/">Startseite</a><a href="{other[1]}">{other[0]}</a></nav></footer>
"""
    return head(path, title, desc, graph, robots="noindex, follow") + "<body>\n" + body + "</body>\n</html>\n"


def page_impressum():
    inner = f"""<section><h2>Angaben gemäß § 5 TMG</h2>
  <p>{logo(extra=' class="legal__logo" loading="lazy" decoding="async"')}</p>
  <p>DAS GmbH</p><p>Heimsheimer Straße 29</p><p>70499 Stuttgart</p><p>Deutschland</p></section>
<section><h2>Kontakt</h2>
  <p>Telefon: <a href="{TEL}">{TEL_TXT}</a></p><p>E-Mail: <a href="{MAIL}">Info@dasmachtdas.de</a></p></section>
<section><h2>Berufsbezeichnung und berufsrechtliche Regelungen</h2>
  <p>Berufsbezeichnung: Karosserie- und Fahrzeugbaumeister</p><p>Geprüft beim SBW</p><p>Verliehen in: Deutschland</p></section>
<section><h2>Haftungsausschluss</h2>
  <p>Die Inhalte unserer Seiten wurden mit größter Sorgfalt erstellt. Für die Richtigkeit, Vollständigkeit und Aktualität der Inhalte können wir jedoch keine Gewähr übernehmen. Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich.</p></section>
<section><h2>Streitschlichtung</h2>
  <p>Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener noreferrer">https://ec.europa.eu/consumers/odr/</a>. Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p></section>"""
    return legal_page("/impressum", "Impressum – DAS GmbH", "Impressum", "Impressum", inner, ("Datenschutz", "/datenschutz"))


def page_datenschutz():
    inner = f"""<section><h2>1. Datenschutz auf einen Blick</h2><h3>Allgemeine Hinweise</h3>
  <p>Die folgenden Hinweise geben einen einfachen Überblick darüber, was mit Ihren personenbezogenen Daten passiert, wenn Sie diese Website besuchen. Personenbezogene Daten sind alle Daten, mit denen Sie persönlich identifiziert werden können.</p></section>
<section><h2>2. Verantwortlicher</h2>
  {logo(extra=' class="legal__logo" loading="lazy" decoding="async"')}
  <p>DAS GmbH</p><p>Heimsheimer Straße 29</p><p>70499 Stuttgart</p>
  <p>E-Mail: <a href="{MAIL}">Info@dasmachtdas.de</a></p><p>Telefon: <a href="{TEL}">{TEL_TXT}</a></p></section>
<section><h2>3. Datenerfassung auf dieser Website</h2><h3>Server-Log-Dateien</h3>
  <p>Der Provider der Seiten erhebt und speichert automatisch Informationen in so genannten Server-Log-Dateien, die Ihr Browser automatisch an uns übermittelt. Dies sind: Browsertyp und Browserversion, verwendetes Betriebssystem, Referrer URL, Hostname des zugreifenden Rechners, Uhrzeit der Serveranfrage, IP-Adresse.</p>
  <p>Eine Zusammenführung dieser Daten mit anderen Datenquellen wird nicht vorgenommen. Die Erfassung dieser Daten erfolgt auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO.</p></section>
<section><h2>4. Kontaktaufnahme per Telefon oder E-Mail</h2>
  <p>Wenn Sie uns per Telefon oder E-Mail kontaktieren, werden Ihre Angaben zwecks Bearbeitung der Anfrage und für den Fall von Anschlussfragen bei uns gespeichert. Diese Daten geben wir nicht ohne Ihre Einwilligung weiter. Die Verarbeitung erfolgt auf Grundlage von Art. 6 Abs. 1 lit. b DSGVO.</p></section>
<section><h2>5. Ihre Rechte</h2>
  <p>Sie haben jederzeit das Recht auf unentgeltliche Auskunft über Ihre gespeicherten personenbezogenen Daten, deren Herkunft und Empfänger und den Zweck der Datenverarbeitung sowie ein Recht auf Berichtigung oder Löschung dieser Daten. Hierzu sowie zu weiteren Fragen zum Thema personenbezogene Daten können Sie sich jederzeit an uns wenden.</p></section>
<section><h2>6. SSL- bzw. TLS-Verschlüsselung</h2>
  <p>Diese Seite nutzt aus Sicherheitsgründen und zum Schutz der Übertragung vertraulicher Inhalte eine SSL- bzw. TLS-Verschlüsselung. Eine verschlüsselte Verbindung erkennen Sie daran, dass die Adresszeile des Browsers von „http://“ auf „https://“ wechselt.</p></section>"""
    return legal_page("/datenschutz", "Datenschutzerklärung – DAS GmbH", "Datenschutzerklärung", "Datenschutz", inner, ("Impressum", "/impressum"))


def page_404():
    graph = [business(), website()]
    body = f"""<header class="lhead"><div class="lhead__bar">
  <a href="/" aria-label="DAS GmbH – Startseite">{logo(extra=' decoding="async"')}</a>
  <a class="btn btn--light btn--sm" href="/"><span>← Zurück zur Startseite</span></a>
</div></header>
<main id="main" class="legal center">
  <p class="eyebrow">Fehler 404</p>
  <h1 class="h-lg" style-none>Seite nicht gefunden</h1>
  <div class="btn-row" style-none>{btn("/", "Zur Startseite", "arrow-right-line", "btn--red")}{btn(TEL, TEL_TXT, "phone-line", "btn--light")}</div>
</main>
"""
    return head("/404", "Seite nicht gefunden – DAS GmbH", "Diese Seite existiert nicht.", graph, robots="noindex, follow") + "<body>\n" + body + "</body>\n</html>\n"


# ---------------------------------------------------------------- text files
def robots():
    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot", "anthropic-ai",
            "PerplexityBot", "Perplexity-User", "Google-Extended", "Googlebot", "Bingbot", "Applebot", "Applebot-Extended",
            "CCBot", "Meta-ExternalAgent", "Amazonbot", "DuckAssistBot", "MistralAI-User", "cohere-ai", "YouBot"]
    out = ["# robots.txt – dasmachtdas.de", "", "User-agent: *", "Allow: /", ""]
    out.append("# KI-Suchbots ausdrücklich erlaubt")
    for b in bots:
        out += [f"User-agent: {b}", "Allow: /", ""]
    out += [f"Sitemap: {SITE}/sitemap.xml", ""]
    return "\n".join(out)


def sitemap():
    urls = [("/", "1.0", "weekly"), ("/jobs", "0.7", "monthly")]
    items = "".join(f"  <url>\n    <loc>{SITE}{p}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>{c}</changefreq>\n    <priority>{pr}</priority>\n  </url>\n" for p, pr, c in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}</urlset>\n'


def llms():
    return f"""# DAS GmbH – Kfz-Werkstatt & Service in Stuttgart

> Professionelle Kfz-Werkstatt in Stuttgart. Wartung, Reparatur, Gutachten, Fahrzeugservice, Reifenwechsel & mehr. Kostenvoranschlag direkt aus der Meisterwerkstatt, Vermittlung an unabhängige VfK-zertifizierte Gutachter.

- Adresse: Heimsheimer Straße 29, 70499 Stuttgart-Weilimdorf
- Telefon (24 h Service-Hotline): 0179 20 333 99
- E-Mail: info@dasmachtdas.de
- Öffnungszeiten: Montag – Freitag 08:00 – 17:00 Uhr, Samstag 11:00 – 14:00 Uhr

## Seiten

- [Startseite]({SITE}/): Leistungen (Gutachten & Bewertung, Technik, Werkstatt, Instandsetzungen, Radwechsel, Service), Über uns, Häufige Fragen, Kostenvoranschlag & Gutachter-Vermittlung, Kontakt, Partner
- [Karriere]({SITE}/jobs): Offene Stellen und Bewerbung

## Ausführlich

- [llms-full.txt]({SITE}/llms-full.txt): Alle Inhalte der Website als Text
"""


def llms_full():
    L = ["# DAS GmbH – Kfz-Werkstatt & Service in Stuttgart", "",
         "> Professionelle Kfz-Werkstatt in Stuttgart. Wartung, Reparatur, Gutachten, Fahrzeugservice, Reifenwechsel & mehr. Jetzt Termin vereinbaren.", "",
         f"Website: {SITE}/", "",
         "## Kontakt", "", "- DAS GmbH, Heimsheimer Straße 29, 70499 Stuttgart", f"- 24 h Service-Hotline: {TEL_TXT}", "- E-Mail: Info@dasmachtdas.de",
         "- WhatsApp: https://wa.me/491721009922", "- Öffnungszeiten: Montag – Freitag 08:00 – 17:00 Uhr; Samstag 11:00 – 14:00 Uhr", "",
         "## KFZ Werkstatt in Stuttgart", "", "Ihr Partner für alles rund ums Auto. Von Achsvermessung bis Aufbereitung – alles aus einer Hand. Schnell, fair, erfahren.", "",
         "- Termin auch am selben Tag", "- Unabhängig & fair", "- Alles aus einer Hand", "",
         "## Auto-Beklebung", "", "Lass dein Auto mit unserer Werbung bekleben und sichere dir 1 Jahr kostenfreie Autowäsche. Dein Fahrzeug wird zur rollenden Werbefläche – professionell beklebt und ein ganzes Jahr lang kostenlos gewaschen. Sichere dir jetzt einen der limitierten Plätze.", "",
         "## Sonderangebot: 40 € RABATT auf Ihren nächsten Service", "", "Nutzen Sie unser limitiertes Angebot und sparen Sie 40 € bei Ihrem nächsten Werkstattbesuch. Gültig auf alle Serviceleistungen — melden Sie sich jetzt an!", "",
         "## Alles rund ums Auto – kompetent und aus einer Hand", ""]
    for _, t, _, _, _, items in SERVICES:
        L += [f"### {t}", ""] + [f"- {i}" for i in items] + [""]
    L += ["## machen wir auch", ""]
    for _, t, st, dsc in ALSO:
        L += [f"### {t} – {st}", "", dsc, ""]
    L += ["## Ihr vertrauensvoller Partner für Kfz-Service in Stuttgart", "",
          "Seit über 20 Jahren steht DAS für erstklassigen Fahrzeugservice mit Leidenschaft und technischer Präzision. Unser erfahrenes Team kombiniert traditionelles Handwerk mit modernster Diagnosetechnik, um jedes Fahrzeug zuverlässig und sicher auf die Straße zu bringen. Dabei ist uns eine ehrliche, transparente Beratung genauso wichtig wie die Qualität unserer Arbeit.", "",
          "## Alles aus einer Hand", ""]
    for i in IA:
        L += [f"### {i[2]}", "", i[3], ""]
    L += ["## Häufige Fragen", ""]
    for q, a in FAQ:
        L += [f"### {q}", "", a, ""]
    L += ["## Kostenvoranschlag? Vermittlung an einen unabhängigen Gutachter? DAS kann beides!", "",
          "### Professioneller Kostenvoranschlag (Direkt von uns)", "",
          "Sie benötigen eine detaillierte Kostenaufstellung für eine Reparatur oder Wartung? Unser Meister-Team erstellt Ihnen einen transparenten, fairen Kostenvoranschlag – schnell, unverbindlich und direkt aus unserer Werkstatt.", ""]
    L += [f"- {t}: {d}" for _, t, d in KV] + [""]
    L += ["### Unabhängiger Gutachter aus der Region (Partner-Vermittlung)", "",
          "Sie brauchen ein offizielles Gutachten? Wir vermitteln Sie an einen unserer geprüften, unabhängigen Partner-Gutachter aus dem Großraum Stuttgart – VfK-zertifiziert, neutral und schnell bei Ihnen vor Ort.", ""]
    L += [f"- {t}: {d}" for _, t, d in GV] + ["", "Einsatzgebiet der Partner: " + ", ".join(AREAS), ""]
    L += ["## Unfall gehabt? Wir sind sofort für Sie da.", "", "Kostenlose Ersteinschätzung am Telefon – im Haftpflichtfall zahlt die gegnerische Versicherung Ihr Gutachten. 0179 20 333 99 – 24 h erreichbar.", ""]
    L += ["## Unsere Partner", "", "Wir arbeiten mit einem starken Netzwerk aus Anwälten, Werkstätten und Dienstleistern zusammen — für Ihre vollständige Schadensabwicklung aus einer Hand.", ""]
    L += [f"- {n}" + (f": {u}" if u else "") for n, u, _ in PARTNERS] + [""]
    L += [f"## Karriere ({SITE}/jobs)", "", "Werden Sie Teil des Teams. Wir suchen engagierte Fachkräfte, die mit Leidenschaft an modernen Fahrzeugen arbeiten und echte Lösungen für echte Menschen schaffen.", ""]
    for jid, title, typ, emp, ic, dsc, tasks, reqs in JOBS:
        L += [f"### {title} ({typ}, Stuttgart)", "", dsc, "", "Ihre Aufgaben:"] + [f"- {t}" for t in tasks] + ["", "Was Sie mitbringen:"] + [f"- {t}" for t in reqs] + [""]
    L += ["### Das erwartet Sie bei uns", ""] + [f"- {t}: {d}" for _, t, d in BENEFITS] + ["", "Bewerbung per E-Mail an info@dasmachtdas.de", ""]
    return "\n".join(L)


def manifest():
    return json.dumps({"name": "DAS GmbH – Kfz-Werkstatt Stuttgart", "short_name": "DAS GmbH", "lang": "de",
                       "start_url": "/", "display": "standalone", "background_color": "#F3F3F1", "theme_color": "#0A0A0A",
                       "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
                                 {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
                                 {"src": "/icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]},
                      ensure_ascii=False, indent=2)


# ---------------------------------------------------------------- write
def clean(html_text):
    # remove helper markers used during authoring
    return html_text.replace(" style-none", "").replace(" novalidate-none", "")


def main():
    if os.path.isdir(OUT):
        for p in glob.glob(os.path.join(OUT, "*.html")):
            os.remove(p)
    os.makedirs(OUT, exist_ok=True)
    # assets
    for sub in ("css", "js"):
        d = os.path.join(OUT, "assets", sub)
        os.makedirs(d, exist_ok=True)
        for f in glob.glob(os.path.join(SRC, "assets", sub, "*")):
            shutil.copy2(f, d)
    pages = {"index.html": page_index(), "jobs.html": page_jobs(), "impressum.html": page_impressum(),
             "datenschutz.html": page_datenschutz(), "404.html": page_404()}
    for name, content in pages.items():
        open(os.path.join(OUT, name), "w", encoding="utf-8").write(clean(content))
    files = {"robots.txt": robots(), "sitemap.xml": sitemap(), "llms.txt": llms(), "llms-full.txt": llms_full(),
             "site.webmanifest": manifest()}
    for name, content in files.items():
        open(os.path.join(OUT, name), "w", encoding="utf-8").write(content)
    print("built", ", ".join(list(pages) + list(files)))


if __name__ == "__main__":
    main()
