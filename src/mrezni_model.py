"""Izračun PDM rasporeda i CPM analiza vremenskih rezervi i kritičnosti."""

import math

import numpy as np

from src.konfiguracija import (
    AKTIVNOSTI,
    NAJRANIJI_POCETCI,
    NAZIVI_AKTIVNOSTI,
    PLANIRANA_TRAJANJA,
    POTPORNE_AKTIVNOSTI,
    VEZE,
    ZAVRSNI_TOKOVI,
)

TOLERANCIJA = 1e-9


def izracunaj_zavrsetak(pocetak, trajanje):
    if trajanje < 0:
        raise ValueError("Trajanje aktivnosti ne smije biti negativno.")
    return pocetak if trajanje == 0 else pocetak + trajanje - 1


def napravi_aktivnost(oznaka, pocetak, trajanje):
    return {
        "aktivnost": oznaka,
        "naziv": NAZIVI_AKTIVNOSTI[oznaka],
        "pocetak": float(pocetak),
        "zavrsetak": float(izracunaj_zavrsetak(pocetak, trajanje)),
        "trajanje": float(trajanje),
    }


def _pocetak_prema_vezi(veza, raspored, trajanja):
    izvor, cilj, tip, pomak = veza
    prethodnik = raspored[izvor]
    trajanje_cilja = trajanja[cilj]

    if tip == "FS":
        return prethodnik["zavrsetak"] + pomak + 1
    if tip == "FF":
        return prethodnik["zavrsetak"] + pomak - trajanje_cilja + 1

    raise ValueError(f"Nepodržan tip veze: {tip}")


def izracunaj_raspored(promijenjena_trajanja=None):
    """Računa najraniji raspored uz FS/FF veze i planirane najranije početke."""
    trajanja = PLANIRANA_TRAJANJA.copy()

    if promijenjena_trajanja:
        nepoznate = set(promijenjena_trajanja) - set(trajanja)
        if nepoznate:
            raise ValueError(f"Nepoznate aktivnosti: {sorted(nepoznate)}")
        trajanja.update(promijenjena_trajanja)

    raspored = {}

    for oznaka in AKTIVNOSTI:
        kandidati = [NAJRANIJI_POCETCI[oznaka]]
        for veza in VEZE:
            if veza[1] == oznaka:
                kandidati.append(_pocetak_prema_vezi(veza, raspored, trajanja))

        raspored[oznaka] = napravi_aktivnost(
            oznaka,
            max(kandidati),
            trajanja[oznaka],
        )

    kraj_projekta = max(raspored[a]["zavrsetak"] for a in ZAVRSNI_TOKOVI)

    for oznaka in POTPORNE_AKTIVNOSTI:
        raspored[oznaka] = napravi_aktivnost(oznaka, 1, kraj_projekta)

    raspored["FINISH"] = napravi_aktivnost("FINISH", kraj_projekta, 0)
    return raspored


def izracunaj_preklapanje(prva, druga):
    pocetak = max(prva["pocetak"], druga["pocetak"])
    zavrsetak = min(prva["zavrsetak"], druga["zavrsetak"])
    return max(0, zavrsetak - pocetak + 1)


def _tezina_veze(veza, trajanja):
    izvor, cilj, tip, pomak = veza

    if tip == "FS":
        return trajanja[izvor] + pomak
    if tip == "FF":
        return trajanja[izvor] - trajanja[cilj] + pomak

    raise ValueError(f"Nepodržan tip veze: {tip}")


def izracunaj_cpm(trajanja=None, raspored=None):
    """Računa PDM ukupnu rezervu (total float) za zadana trajanja."""
    trajanja = PLANIRANA_TRAJANJA.copy() if trajanja is None else dict(trajanja)
    raspored = izracunaj_raspored(trajanja) if raspored is None else raspored

    najraniji = {a: raspored[a]["pocetak"] for a in AKTIVNOSTI}
    kraj_mreze = max(raspored[a]["zavrsetak"] for a in ZAVRSNI_TOKOVI)
    najkasniji = {a: math.inf for a in AKTIVNOSTI}

    # Završne aktivnosti moraju završiti najkasnije u trenutku kraja mreže.
    for a in ZAVRSNI_TOKOVI:
        najkasniji[a] = kraj_mreze - trajanja[a] + 1

    # Generalizirani backward pass za FS/FF veze.
    for izvor in reversed(AKTIVNOSTI):
        kandidati = []
        for veza in VEZE:
            if veza[0] == izvor:
                cilj = veza[1]
                kandidati.append(najkasniji[cilj] - _tezina_veze(veza, trajanja))

        if kandidati:
            najkasniji[izvor] = min(najkasniji[izvor], *kandidati)

    aktivnosti = {}
    for a in AKTIVNOSTI:
        es = najraniji[a]
        ef = raspored[a]["zavrsetak"]
        ls = najkasniji[a]
        lf = ls + trajanja[a] - 1
        rezerva = ls - es
        if rezerva < -TOLERANCIJA:
            raise ValueError(f"Negativna CPM rezerva za {a}: {rezerva}")
        if abs(rezerva) <= TOLERANCIJA:
            rezerva = 0.0
        aktivnosti[a] = {
            "najraniji_pocetak": float(es),
            "najraniji_zavrsetak": float(ef),
            "najkasniji_pocetak": float(ls),
            "najkasniji_zavrsetak": float(lf),
            "ukupna_rezerva": float(rezerva),
            "kriticna": bool(np.isclose(rezerva, 0.0, atol=TOLERANCIJA, rtol=0.0)),
        }

    # Kritična je mrežna veza koja je aktivna (bez slaka) i povezuje
    # dvije kritične aktivnosti. Za par s više uvjeta dovoljno je da je
    # barem jedan uvjet kritičan.
    kriticne_veze = set()
    detalji_veza = []
    for veza in VEZE:
        izvor, cilj, tip, pomak = veza
        slack = najraniji[cilj] - najraniji[izvor] - _tezina_veze(veza, trajanja)
        kriticna = (
            aktivnosti[izvor]["kriticna"]
            and aktivnosti[cilj]["kriticna"]
            and np.isclose(slack, 0.0, atol=TOLERANCIJA, rtol=0.0)
        )
        if kriticna:
            kriticne_veze.add((izvor, cilj))
        detalji_veza.append({
            "izvor": izvor,
            "cilj": cilj,
            "tip": tip,
            "pomak": pomak,
            "slack_veze": float(max(0.0, slack)),
            "kriticna": bool(kriticna),
        })

    for a in ZAVRSNI_TOKOVI:
        if aktivnosti[a]["kriticna"] and np.isclose(
            raspored[a]["zavrsetak"], kraj_mreze, atol=TOLERANCIJA, rtol=0.0
        ):
            kriticne_veze.add((a, "FINISH"))

    return {
        "aktivnosti": aktivnosti,
        "veze": detalji_veza,
        "kriticne_veze": kriticne_veze,
        "kraj_mreze": float(kraj_mreze),
    }
