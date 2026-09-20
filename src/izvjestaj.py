"""Ispis i spremanje tabličnih rezultata."""

import csv
from pathlib import Path

from src.konfiguracija import REDOSLIJED_ISPISA, ROK_PROJEKTA


def mapa_izlaza():
    putanja = Path(__file__).resolve().parent.parent / "outputs"
    putanja.mkdir(parents=True, exist_ok=True)
    return putanja


def spremi_csv(putanja, retci):
    if not retci:
        return

    with putanja.open("w", encoding="utf-8-sig", newline="") as datoteka:
        pisac = csv.DictWriter(datoteka, fieldnames=retci[0].keys())
        pisac.writeheader()
        pisac.writerows(retci)


def spremi_raspored(raspored, cpm):
    putanja = mapa_izlaza() / "s0_raspored.csv"
    retci = []

    for oznaka in REDOSLIJED_ISPISA:
        aktivnost = raspored[oznaka]
        redak = {
            "aktivnost": oznaka,
            "naziv": aktivnost["naziv"],
            "pocetak": aktivnost["pocetak"],
            "zavrsetak": aktivnost["zavrsetak"],
            "trajanje": aktivnost["trajanje"],
            "ukupna_rezerva": "",
            "kriticna": "",
        }

        if oznaka in cpm["aktivnosti"]:
            redak["ukupna_rezerva"] = cpm["aktivnosti"][oznaka]["ukupna_rezerva"]
            redak["kriticna"] = "Da" if cpm["aktivnosti"][oznaka]["kriticna"] else "Ne"

        retci.append(redak)

    spremi_csv(putanja, retci)
    return putanja


def prikazi_raspored(raspored, cpm):
    print("\nS0 - planirani raspored bez rizika")
    print(f"{'ID':<8}{'Početak':>10}{'Završetak':>12}{'Trajanje':>11}{'TF':>8}")
    print("-" * 49)

    for oznaka in REDOSLIJED_ISPISA:
        red = raspored[oznaka]
        tf = cpm["aktivnosti"].get(oznaka, {}).get("ukupna_rezerva", "-")
        tf_tekst = f"{tf:g}" if isinstance(tf, (int, float)) else tf
        pocetak = f"M{red['pocetak']:g}"
        zavrsetak = f"M{red['zavrsetak']:g}"
        print(
            f"{oznaka:<8}{pocetak:>10}{zavrsetak:>12}"
            f"{red['trajanje']:>11g}{tf_tekst:>8}"
        )

    kraj = raspored["FINISH"]["zavrsetak"]
    print(f"\nPlanirani završetak projekta: M{kraj:g}")
    print(f"Završetak unutar M{ROK_PROJEKTA:g}: {'DA' if kraj <= ROK_PROJEKTA else 'NE'}")
