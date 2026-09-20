"""Ulazni parametri rizika za Monte Carlo simulaciju.

Brojčane vjerojatnosti i trokutasti učinci radne su procjene autorice tamo
gdje projektna dokumentacija ne daje kvantitativne parametre.
"""

VJEROJATNOSTI = {
    "Niska": 0.15,
    "Srednja": 0.45,
    "Visoka": 0.80,
}


def ucinak(cilj, minimum, najvjerojatnije, maksimum):
    return {
        "cilj": cilj,
        "minimum": minimum,
        "najvjerojatnije": najvjerojatnije,
        "maksimum": maksimum,
    }


# Svaki rizik ima jednu vjerojatnost nastupa i jedan ili više učinaka.
# Ako rizik s više učinaka nastupi, događaj se izvlači jednom, a veličina
# posljedice zasebno za svaku zahvaćenu aktivnost.
RIZICI = (
    {
        "id": "T1",
        "vrsta": "Prijetnja",
        "naziv": "Nizak odaziv dionika",
        "kvalitativna_vjerojatnost": "Srednja",
        "kvalitativni_utjecaj": "Srednji",
        "vjerojatnost": VJEROJATNOSTI["Srednja"],
        "ucinci": (
            ucinak("A1.1", 0.50, 1.00, 2.00),
            ucinak("A1.2", 0.25, 0.50, 1.00),
        ),
        "ukljucen": True,
        "obrazlozenje": "Slabiji odaziv može produljiti prikupljanje podataka u visokom obrazovanju i, u manjoj mjeri, analizu potreba poduzeća.",
    },
    {
        "id": "T2",
        "vrsta": "Prijetnja",
        "naziv": "Neusklađenost konceptualnog modela",
        "kvalitativna_vjerojatnost": "Niska",
        "kvalitativni_utjecaj": "Visok",
        "vjerojatnost": VJEROJATNOSTI["Niska"],
        "ucinci": (ucinak("A2.1", 0.50, 1.50, 3.00),),
        "ukljucen": True,
        "obrazlozenje": "Ponavljanje validacije, izmjena zahtjeva i dorada koncepta.",
    },
    {
        "id": "T3",
        "vrsta": "Prijetnja",
        "naziv": "Poteškoće integracije i kvalitete podataka",
        "kvalitativna_vjerojatnost": "Srednja",
        "kvalitativni_utjecaj": "Visok",
        "vjerojatnost": VJEROJATNOSTI["Srednja"],
        "ucinci": (
            ucinak("A3.1", 1.00, 2.00, 4.00),
            ucinak("A4.1", 0.50, 1.00, 2.00),
        ),
        "ukljucen": True,
        "obrazlozenje": "Problemi s dostupnošću, formatom ili kvalitetom podataka mogu zahtijevati dodatno čišćenje i integraciju u prototipu te prilagodbu podatkovne podloge za primjere uporabe.",
    },
    {
        "id": "T4",
        "vrsta": "Prijetnja",
        "naziv": "Niska prihvaćenost nadzornih ploča",
        "kvalitativna_vjerojatnost": "Srednja",
        "kvalitativni_utjecaj": "Srednji",
        "vjerojatnost": VJEROJATNOSTI["Srednja"],
        "ucinci": (
            ucinak("A3.2", 0.50, 1.00, 2.00),
            ucinak("A4.1", 0.25, 0.50, 1.00),
        ),
        "ukljucen": True,
        "obrazlozenje": "Slabija prihvaćenost može zahtijevati dodatno korisničko testiranje i doradu sučelja te manju prilagodbu načina primjene rješenja u konkretnim slučajevima uporabe.",
    },
    {
        "id": "T5",
        "vrsta": "Prijetnja",
        "naziv": "Nedovoljna pouzdanost AI modela",
        "kvalitativna_vjerojatnost": "Srednja",
        "kvalitativni_utjecaj": "Visok",
        "vjerojatnost": VJEROJATNOSTI["Srednja"],
        "ucinci": (
            ucinak("A4.1", 1.00, 2.00, 4.00),
            ucinak("A3.2", 0.25, 0.50, 1.00),
        ),
        "ukljucen": True,
        "obrazlozenje": "Nedovoljno pouzdani izlazi mogu zahtijevati ponovno treniranje ili prilagodbu modela, dodatnu evaluaciju performansi i ponovnu validaciju u prototipu.",
    },
    {
        "id": "T6",
        "vrsta": "Prijetnja",
        "naziv": "Kašnjenje publikacija i projektnih prijava",
        "kvalitativna_vjerojatnost": "Srednja",
        "kvalitativni_utjecaj": "Nizak",
        "vjerojatnost": VJEROJATNOSTI["Srednja"],
        "ucinci": (ucinak("A5.2", 0.25, 0.50, 1.50),),
        "ukljucen": True,
        "obrazlozenje": "Dorada rada, recenzijski zahtjevi ili nepovoljan rok mogu odgoditi završnu diseminaciju i prijave.",
    },
    {
        "id": "T7",
        "vrsta": "Prijetnja",
        "naziv": "Nejasno tržišno pozicioniranje ili potražnja",
        "kvalitativna_vjerojatnost": "Niska",
        "kvalitativni_utjecaj": "Visok",
        "vjerojatnost": VJEROJATNOSTI["Niska"],
        "ucinci": (ucinak("A5.1", 0.25, 0.75, 1.50),),
        "ukljucen": True,
        "obrazlozenje": "Dodatna tržišna analiza i prilagodba strategije komercijalizacije mogu produljiti A5.1.",
    },
    {
        "id": "T8",
        "vrsta": "Prijetnja",
        "naziv": "Problemi koordinacije projekta",
        "kvalitativna_vjerojatnost": "Niska",
        "kvalitativni_utjecaj": "Srednji",
        "vjerojatnost": VJEROJATNOSTI["Niska"],
        "ucinci": (
            ucinak("A2.1", 0.10, 0.20, 0.40),
            ucinak("A3.1", 0.10, 0.25, 0.50),
            ucinak("A3.2", 0.10, 0.25, 0.50),
            ucinak("A4.1", 0.10, 0.25, 0.50),
            ucinak("A5.1", 0.10, 0.30, 0.60),
            ucinak("A5.2", 0.10, 0.30, 0.60),
        ),
        "ukljucen": True,
        "obrazlozenje": (
            "Kašnjenje odluka, potvrda, razmjene informacija ili primopredaje "
            "između projektnih tokova može produljiti aktivnosti koje ovise o "
            "koordinaciji više partnera ili o rezultatima prethodnih aktivnosti."
        ),
    },
    {
        "id": "T9",
        "vrsta": "Prijetnja",
        "naziv": "Nedovoljna skalabilnost prototipa",
        "kvalitativna_vjerojatnost": "Niska",
        "kvalitativni_utjecaj": "Visok",
        "vjerojatnost": VJEROJATNOSTI["Niska"],
        "ucinci": (
            ucinak("A3.2", 1.00, 2.00, 4.00),
            ucinak("A3.1", 0.50, 1.00, 2.00),
        ),
        "ukljucen": True,
        "obrazlozenje": "Problem skalabilnosti može zahtijevati arhitekturne dorade prototipa i zatim dodatno testiranje i ponovnu validaciju.",
    },
    {
        "id": "P1",
        "vrsta": "Prilika",
        "naziv": "Ranija dostupnost tržišnih i partnerskih podataka",
        "kvalitativna_vjerojatnost": "Srednja - procjena autorice",
        "kvalitativni_utjecaj": "Srednji - procjena autorice",
        "vjerojatnost": VJEROJATNOSTI["Srednja"],
        "ucinci": (
            ucinak("A5.1", 0.25, 0.50, 1.00),
            ucinak("A5.2", 0.10, 0.25, 0.50),
        ),
        "ukljucen": True,
        "obrazlozenje": "Raniji tržišni i partnerski podatci mogu ubrzati razvoj strategije suradnje te u manjoj mjeri olakšati završnu diseminaciju i umrežavanje.",
    },
)


def ucinci_rizika(rizik):
    return rizik["ucinci"]


def provjeri_parametre_rizika():
    dozvoljeni_ciljevi = {
        "A1.1", "A1.2", "A2.1", "A3.1", "A3.2",
        "A4.1", "A5.1", "A5.2",
    }

    for rizik in RIZICI:
        if rizik["vrsta"] not in {"Prijetnja", "Prilika"}:
            raise ValueError(f"{rizik['id']}: nepoznata vrsta rizika.")
        if not 0 <= rizik["vjerojatnost"] <= 1:
            raise ValueError(f"{rizik['id']}: vjerojatnost mora biti između 0 i 1.")
        if not rizik["ucinci"]:
            raise ValueError(f"{rizik['id']}: mora imati barem jedan učinak.")

        for ucinak_rizika in rizik["ucinci"]:
            a = ucinak_rizika["minimum"]
            m = ucinak_rizika["najvjerojatnije"]
            b = ucinak_rizika["maksimum"]
            if not 0 <= a <= m <= b:
                raise ValueError(f"{rizik['id']}: neispravni trokutasti parametri.")
            if ucinak_rizika["cilj"] not in dozvoljeni_ciljevi:
                raise ValueError(f"{rizik['id']}: nepoznat cilj {ucinak_rizika['cilj']}.")

    return True
