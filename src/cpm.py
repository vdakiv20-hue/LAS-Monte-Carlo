"""CPM/PDM izračun najranijih i najkasnijih termina te ukupne rezerve."""

import math

import numpy as np

from src.konfiguracija import PLANIRANA_TRAJANJA
from src.mreza import AKTIVNOSTI, VEZE, ZAVRSNI_TOKOVI
from src.mrezni_model import izracunaj_raspored

TOLERANCIJA = 1e-9


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
