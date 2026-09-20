"""Projektni podaci, definicija mreže i postavke simulacije LAS."""

BROJ_ITERACIJA = 50_000
SJEME = 42
ROK_PROJEKTA = 36.0

PLANIRANA_TRAJANJA = {
    "A1.1": 5.0,
    "A1.2": 5.0,
    "A2.1": 7.0,
    "A3.1": 16.0,
    "A3.2": 6.0,
    "A4.1": 32.0,
    "A5.1": 17.0,
    "A5.2": 33.0,
}

NAZIVI_AKTIVNOSTI = {
    "A1.1": "Analiza znanstvenih rezultata, etičkog i pravnog okvira te potreba dionika u visokom obrazovanju",
    "A1.2": "Analiza potreba poduzeća i neobrazovnih institucija za analitikom učenja",
    "A2.1": "Razvoj koncepta cjelovitog sustava za analitiku učenja",
    "A3.1": "Razvoj prototipa cjelovitog sustava za analitiku učenja",
    "A3.2": "Testiranje i validacija prototipa cjelovitog sustava za analitiku učenja",
    "A4.1": "Primjeri uporabe iz visokog obrazovanja i poduzeća",
    "A5.1": "Nastavak istraživanja, strategija suradnje, komercijalizacija i intelektualno vlasništvo",
    "A5.2": "Diseminacija istraživačkih rezultata i umrežavanje",
    "A6.1": "Upravljanje projektom",
    "A6.2": "Horizontalne aktivnosti",
    "A6.3": "Promocija i vidljivost",
    "FINISH": "Završna prekretnica projekta",
}

POTPORNE_AKTIVNOSTI = ("A6.1", "A6.2", "A6.3")

REDOSLIJED_ISPISA = (
    "A1.1", "A1.2", "A2.1", "A3.1", "A3.2", "A4.1",
    "A5.1", "A5.2", "A6.1", "A6.2", "A6.3", "FINISH",
)

# Aktivnosti su u topološkom redoslijedu: prethodnici dolaze prije sljedbenika.
AKTIVNOSTI = (
    "A1.1", "A1.2", "A2.1", "A3.1",
    "A3.2", "A4.1", "A5.1", "A5.2",
)

# Najraniji planirani počeci iz Ganttova dijagrama.
NAJRANIJI_POCETCI = {
    "A1.1": 2.0,
    "A1.2": 3.0,
    "A2.1": 6.0,
    "A3.1": 13.0,
    "A3.2": 27.0,
    "A4.1": 4.0,
    "A5.1": 20.0,
    "A5.2": 3.0,
}

# tip: FS = finish-to-start, FF = finish-to-finish.
# pomak se izražava u mjesecima. Negativan pomak dopušta preklapanje.
VEZE = (
    ("A1.1", "A2.1", "FS", -1.0),
    ("A1.2", "A2.1", "FS", -2.0),
    ("A2.1", "A3.1", "FS", 0.0),
    ("A3.1", "A3.2", "FS", -2.0),
    ("A3.1", "A3.2", "FF", 0.0),
    ("A3.1", "A4.1", "FF", 0.0),
    ("A4.1", "A5.1", "FF", 0.0),
    ("A3.2", "A5.2", "FF", 0.0),
    ("A4.1", "A5.2", "FF", 0.0),
)

ZAVRSNI_TOKOVI = ("A5.1", "A5.2")
