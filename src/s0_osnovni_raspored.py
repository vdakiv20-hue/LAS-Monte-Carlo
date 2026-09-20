"""Scenarij S0: deterministički raspored i CPM analiza mreže."""

from src.grafovi import nacrtaj_s0_mrezu
from src.izvjestaj import mapa_izlaza, prikazi_raspored, spremi_raspored
from src.mrezni_model import izracunaj_cpm, izracunaj_preklapanje, izracunaj_raspored

OCEKIVANI_RASPONI = {
    "A1.1": (2, 6), "A1.2": (3, 7), "A2.1": (6, 12), "A3.1": (13, 28),
    "A3.2": (27, 32), "A4.1": (4, 35), "A5.1": (20, 36), "A5.2": (3, 35),
    "A6.1": (1, 36), "A6.2": (1, 36), "A6.3": (1, 36), "FINISH": (36, 36),
}

OCEKIVANE_REZERVE = {
    "A1.1": 4.0, "A1.2": 4.0, "A2.1": 4.0, "A3.1": 4.0,
    "A3.2": 4.0, "A4.1": 1.0, "A5.1": 0.0, "A5.2": 1.0,
}


def provjeri_s0(raspored, cpm):
    """Kontrolne provjere službenog Gantta, veza i CPM rezervi."""
    for oznaka, ocekivano in OCEKIVANI_RASPONI.items():
        stvarno = (raspored[oznaka]["pocetak"], raspored[oznaka]["zavrsetak"])
        assert stvarno == ocekivano, f"Neispravan S0 raspon za {oznaka}: {stvarno}"

    for oznaka, ocekivano in OCEKIVANE_REZERVE.items():
        stvarno = cpm["aktivnosti"][oznaka]["ukupna_rezerva"]
        assert abs(stvarno - ocekivano) < 1e-9, f"Neispravan TF za {oznaka}: {stvarno}"

    assert izracunaj_preklapanje(raspored["A1.1"], raspored["A2.1"]) == 1
    assert izracunaj_preklapanje(raspored["A1.2"], raspored["A2.1"]) == 2
    assert izracunaj_preklapanje(raspored["A3.1"], raspored["A3.2"]) == 2

    # Kontrolni primjeri prijenosa kašnjenja kroz mrežu.
    assert izracunaj_raspored({"A2.1": 12})["FINISH"]["zavrsetak"] == 37
    assert izracunaj_raspored({"A1.2": 10})["FINISH"]["zavrsetak"] == 37


def pokreni_s0():
    raspored = izracunaj_raspored()
    cpm = izracunaj_cpm(raspored=raspored)
    provjeri_s0(raspored, cpm)

    prikazi_raspored(raspored, cpm)
    putanja_rasporeda = spremi_raspored(raspored, cpm)
    putanja_dijagrama = mapa_izlaza() / "s0_mrezni_dijagram.png"
    nacrtaj_s0_mrezu(raspored, cpm, putanja_dijagrama)

    kriticne = [a for a, podaci in cpm["aktivnosti"].items() if podaci["kriticna"]]
    print(f"Kritične aktivnosti prema CPM-u: {', '.join(kriticne)}")
    print("Provjera mrežne logike i CPM izračuna: OK")
    print(f"Raspored: {putanja_rasporeda}")
    print(f"Mrežni dijagram: {putanja_dijagrama}")
