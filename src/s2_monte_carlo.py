"""Scenarij S2: usporedba rezultata nakon odgovora na rizike."""

import numpy as np

from src.grafovi import (
    nacrtaj_usporedbu_pokazatelja,
    nacrtaj_usporedbu_s_krivulja,
)
from src.izvjestaj import mapa_izlaza, spremi_csv
from src.konfiguracija import BROJ_ITERACIJA, PLANIRANA_TRAJANJA, ROK_PROJEKTA, SJEME
from src.mrezni_model import izracunaj_raspored
from src.odgovori_na_rizike import (
    FAKTOR_POVECANJA_VJEROJATNOSTI_PRILIKE,
    FAKTOR_PREOSTALE_VJEROJATNOSTI,
    FAKTOR_PREOSTALOG_UCINKA,
    MJERE_MITIGACIJE,
    MJERE_POBOLJSANJA_PRILIKA,
    provjeri_mjere_mitigacije,
    provjeri_odgovore_na_prilike,
)
from src.rizici import RIZICI, provjeri_parametre_rizika, ucinci_rizika
from src.s1_monte_carlo import simuliraj_zavrsetke
from src.simulacija import izracunaj_rezultate

POKAZATELJI_USPOREDBE = {
    "Prosječni završetak": "prosjecni_zavrsetak",
    "Standardna devijacija": "standardna_devijacija",
    "P50": "p50",
    "P80": "p80",
    "P90": "p90",
    "Vjerojatnost završetka u roku": "vjerojatnost_zavrsetka_u_roku",
    "Očekivano kašnjenje": "ocekivano_kasnjenje",
    "P80 vremenska rezerva": "potrebna_rezerva_p80",
}


def parametri_nakon_odgovora(rizik, faktor_p=None, faktor_ucinka=None):
    """Vraća parametre rizika nakon odgovora; faktori se mogu mijenjati za osjetljivost."""
    if rizik["vrsta"] == "Prilika":
        return (
            min(1.0, rizik["vjerojatnost"] * FAKTOR_POVECANJA_VJEROJATNOSTI_PRILIKE),
            1.0,
            MJERE_POBOLJSANJA_PRILIKA[rizik["id"]],
        )

    faktor_p = FAKTOR_PREOSTALE_VJEROJATNOSTI if faktor_p is None else faktor_p
    faktor_ucinka = FAKTOR_PREOSTALOG_UCINKA if faktor_ucinka is None else faktor_ucinka
    return (
        rizik["vjerojatnost"] * faktor_p,
        faktor_ucinka,
        MJERE_MITIGACIJE[rizik["id"]],
    )


def primijeni_odgovore_na_rizike(generator, faktor_p=None, faktor_ucinka=None):
    trajanja = PLANIRANA_TRAJANJA.copy()
    for rizik in RIZICI:
        vjerojatnost, faktor, _ = parametri_nakon_odgovora(rizik, faktor_p, faktor_ucinka)
        if not rizik["ukljucen"] or generator.random() >= vjerojatnost:
            continue

        predznak = -1.0 if rizik["vrsta"] == "Prilika" else 1.0
        for ucinak in ucinci_rizika(rizik):
            vrijednost = predznak * float(generator.triangular(
                ucinak["minimum"] * faktor,
                ucinak["najvjerojatnije"] * faktor,
                ucinak["maksimum"] * faktor,
            ))
            cilj = ucinak["cilj"]
            trajanja[cilj] = max(0.0, trajanja[cilj] + vrijednost)

    return trajanja


def simuliraj_s2(broj_iteracija=BROJ_ITERACIJA, sjeme=SJEME, faktor_p=None, faktor_ucinka=None):
    generator = np.random.default_rng(sjeme)
    zavrsetci = np.empty(broj_iteracija)

    for i in range(broj_iteracija):
        trajanja = primijeni_odgovore_na_rizike(generator, faktor_p, faktor_ucinka)
        zavrsetci[i] = izracunaj_raspored(trajanja)["FINISH"]["zavrsetak"]

    return zavrsetci


def izvedi_s2(broj_iteracija=BROJ_ITERACIJA, sjeme=SJEME):
    provjeri_parametre_rizika()
    provjeri_mjere_mitigacije(RIZICI)
    provjeri_odgovore_na_prilike(RIZICI)
    zavrsetci = simuliraj_s2(broj_iteracija, sjeme)
    return izracunaj_rezultate(zavrsetci, broj_iteracija, sjeme), zavrsetci


def pripremi_ulaze_s2():
    retci = []
    for rizik in RIZICI:
        if not rizik["ukljucen"]:
            continue

        p_nakon, faktor, odgovor = parametri_nakon_odgovora(rizik)
        for i, ucinak in enumerate(ucinci_rizika(rizik)):
            retci.append({
                "id": rizik["id"], "vrsta": rizik["vrsta"], "naziv": rizik["naziv"],
                "tip_ucinka": "glavni" if i == 0 else "dodatni", "cilj": ucinak["cilj"],
                "vjerojatnost_prije": rizik["vjerojatnost"], "vjerojatnost_nakon": round(p_nakon, 6),
                "minimum_prije": ucinak["minimum"], "minimum_nakon": round(ucinak["minimum"] * faktor, 6),
                "najvjerojatnije_prije": ucinak["najvjerojatnije"],
                "najvjerojatnije_nakon": round(ucinak["najvjerojatnije"] * faktor, 6),
                "maksimum_prije": ucinak["maksimum"], "maksimum_nakon": round(ucinak["maksimum"] * faktor, 6),
                "odgovor": odgovor,
            })
    return retci


def usporedi_s1_s2(s1, s2):
    return [
        {
            "pokazatelj": naziv,
            "s1_prije_odgovora": s1[kljuc],
            "s2_nakon_odgovora": s2[kljuc],
            "promjena_s2_minus_s1": s2[kljuc] - s1[kljuc],
        }
        for naziv, kljuc in POKAZATELJI_USPOREDBE.items()
    ]


def analiza_osjetljivosti(broj_iteracija=20_000, sjeme=SJEME):
    """Mala provjera koliko S2 ovisi o pretpostavljenom preostalom faktoru 0,70."""
    retci = []
    for faktor in (0.60, 0.70, 0.80):
        zavrsetci = simuliraj_s2(broj_iteracija, sjeme, faktor_p=faktor, faktor_ucinka=faktor)
        rezultati = izracunaj_rezultate(zavrsetci, broj_iteracija, sjeme)
        retci.append({
            "preostali_faktor_prijetnji": faktor,
            "broj_iteracija": broj_iteracija,
            "p80": rezultati["p80"],
            "vjerojatnost_zavrsetka_u_roku": rezultati["vjerojatnost_zavrsetka_u_roku"],
            "ocekivano_kasnjenje": rezultati["ocekivano_kasnjenje"],
        })
    return retci


def provjeri_s2(s1, s2):
    assert s2["prosjecni_zavrsetak"] < s1["prosjecni_zavrsetak"]
    assert s2["p80"] < s1["p80"]
    assert s2["vjerojatnost_zavrsetka_u_roku"] > s1["vjerojatnost_zavrsetka_u_roku"]
    assert s2["ocekivano_kasnjenje"] < s1["ocekivano_kasnjenje"]


def spremi_s2(s1, s2, zavrsetci_s1, zavrsetci_s2):
    izlaz = mapa_izlaza()
    putanje = {
        "sazetak": izlaz / "s2_sazetak.csv",
        "ulazi": izlaz / "s2_ulazi_i_mjere.csv",
        "usporedba": izlaz / "usporedba_s1_s2.csv",
        "osjetljivost": izlaz / "s2_osjetljivost_faktora.csv",
        "s_krivulje": izlaz / "usporedba_s1_s2_s_krivulje.png",
        "pokazatelji": izlaz / "usporedba_s1_s2_pokazatelji.png",
    }

    spremi_csv(putanje["sazetak"], [{"pokazatelj": k, "vrijednost": v} for k, v in s2.items()])
    spremi_csv(putanje["ulazi"], pripremi_ulaze_s2())
    spremi_csv(putanje["usporedba"], usporedi_s1_s2(s1, s2))
    spremi_csv(putanje["osjetljivost"], analiza_osjetljivosti())
    nacrtaj_usporedbu_s_krivulja(zavrsetci_s1, zavrsetci_s2, s1, s2, putanje["s_krivulje"])
    nacrtaj_usporedbu_pokazatelja(s1, s2, putanje["pokazatelji"])
    return putanje


def pokreni_s2():
    _, zavrsetci_s1 = simuliraj_zavrsetke(BROJ_ITERACIJA, SJEME, spremi_retke=False)
    s1 = izracunaj_rezultate(zavrsetci_s1, BROJ_ITERACIJA, SJEME)
    s2, zavrsetci_s2 = izvedi_s2()
    provjeri_s2(s1, s2)
    putanje = spremi_s2(s1, s2, zavrsetci_s1, zavrsetci_s2)

    print("\nUsporedba prije i nakon odgovora na rizike")
    print(f"Prosječni završetak: M{s1['prosjecni_zavrsetak']:.2f} → M{s2['prosjecni_zavrsetak']:.2f}")
    print(f"Standardna devijacija: {s1['standardna_devijacija']:.2f} → {s2['standardna_devijacija']:.2f}")
    print(f"P50: M{s1['p50']:.2f} → M{s2['p50']:.2f}")
    print(f"P80: M{s1['p80']:.2f} → M{s2['p80']:.2f}")
    print(f"P90: M{s1['p90']:.2f} → M{s2['p90']:.2f}")
    print(
        f"Završetak u roku (M{ROK_PROJEKTA:g}): "
        f"{s1['vjerojatnost_zavrsetka_u_roku']:.1%} → {s2['vjerojatnost_zavrsetka_u_roku']:.1%}"
    )
    print(f"Očekivano kašnjenje: {s1['ocekivano_kasnjenje']:.2f} → {s2['ocekivano_kasnjenje']:.2f} mj.")
    print(f"P80 rezerva: {s1['potrebna_rezerva_p80']:.2f} → {s2['potrebna_rezerva_p80']:.2f} mj.")
    print(f"Najkasniji završetak: M{s1['najkasniji_zavrsetak']:.2f} → M{s2['najkasniji_zavrsetak']:.2f}")
    print(f"Rezultati: {putanje['usporedba'].parent}")
