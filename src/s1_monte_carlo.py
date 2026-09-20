"""Scenarij S1: Monte Carlo analiza prije dodatnih odgovora na rizike."""

from collections import Counter

import numpy as np

from src.grafovi import (
    nacrtaj_analizu_prilike,
    nacrtaj_histogram,
    nacrtaj_indeks_kriticnosti,
    nacrtaj_konvergenciju,
    nacrtaj_s_krivulju,
    nacrtaj_tornado,
    nacrtaj_utjecaj_na_rok,
)
from src.izvjestaj import mapa_izlaza, spremi_csv
from src.konfiguracija import (
    AKTIVNOSTI,
    BROJ_ITERACIJA,
    PLANIRANA_TRAJANJA,
    ROK_PROJEKTA,
    SJEME,
    VEZE,
    ZAVRSNI_TOKOVI,
)
from src.mrezni_model import izracunaj_cpm, izracunaj_raspored
from src.rizici import RIZICI, provjeri_parametre_rizika, ucinci_rizika
from src.simulacija import izracunaj_rezultate


def kljuc_ucinka(rizik, indeks, cilj):
    return rizik["id"] if indeks == 0 else f"{rizik['id']}_{cilj}"


def primijeni_rizike(generator, izostavljeni_rizik=None):
    trajanja = PLANIRANA_TRAJANJA.copy()
    ostvareni_ucinci = {}

    for rizik in RIZICI:
        ucinci = ucinci_rizika(rizik)
        for i, ucinak in enumerate(ucinci):
            ostvareni_ucinci[kljuc_ucinka(rizik, i, ucinak["cilj"])] = 0.0

        nastupio = rizik["ukljucen"] and generator.random() < rizik["vjerojatnost"]
        if not nastupio:
            continue

        # Vrijednosti se generiraju i kod leave-one-out analize radi istog slučajnog toka.
        vrijednosti = [
            float(generator.triangular(u["minimum"], u["najvjerojatnije"], u["maksimum"]))
            for u in ucinci
        ]
        if rizik["id"] == izostavljeni_rizik:
            continue

        predznak = -1.0 if rizik["vrsta"] == "Prilika" else 1.0
        for i, (ucinak, vrijednost) in enumerate(zip(ucinci, vrijednosti)):
            vrijednost *= predznak
            cilj = ucinak["cilj"]
            trajanja[cilj] = max(0.0, trajanja[cilj] + vrijednost)
            ostvareni_ucinci[kljuc_ucinka(rizik, i, cilj)] = vrijednost

    return trajanja, ostvareni_ucinci



def simuliraj_zavrsetke(
    broj_iteracija=BROJ_ITERACIJA,
    sjeme=SJEME,
    izostavljeni_rizik=None,
    spremi_retke=False,
    brojaci_aktivnosti=None,
    brojaci_veza=None,
):
    if broj_iteracija <= 0:
        raise ValueError("Broj iteracija mora biti veći od nule.")

    generator = np.random.default_rng(sjeme)
    zavrsetci = np.empty(broj_iteracija)
    retci = [] if spremi_retke else None
    prati_cpm = brojaci_aktivnosti is not None and brojaci_veza is not None

    for i in range(broj_iteracija):
        trajanja, ucinci = primijeni_rizike(generator, izostavljeni_rizik)
        raspored = izracunaj_raspored(trajanja)
        zavrsetci[i] = raspored["FINISH"]["zavrsetak"]

        if prati_cpm:
            cpm = izracunaj_cpm(trajanja, raspored)
            brojaci_aktivnosti.update(
                a for a in AKTIVNOSTI if cpm["aktivnosti"][a]["kriticna"]
            )
            brojaci_veza.update(cpm["kriticne_veze"])

        if spremi_retke:
            redak = {
                "iteracija": i + 1,
                "zavrsetak_projekta": zavrsetci[i],
                "prekoracen_rok": int(zavrsetci[i] > ROK_PROJEKTA),
            }
            redak.update({f"{k}_ucinak": v for k, v in ucinci.items()})
            retci.append(redak)

    return retci, zavrsetci


def pripremi_indeks_kriticnosti(brojaci_aktivnosti, brojaci_veza, broj_iteracija):
    aktivnosti = [
        {
            "aktivnost": a,
            "broj_iteracija": brojaci_aktivnosti[a],
            "indeks_kriticnosti": brojaci_aktivnosti[a] / broj_iteracija,
        }
        for a in AKTIVNOSTI
    ]

    # Parovi dolaze iz modela; više uvjeta između istog para daje jedan redak.
    parovi = []
    for izvor, cilj, *_ in VEZE:
        if (izvor, cilj) not in parovi:
            parovi.append((izvor, cilj))
    parovi.extend((a, "FINISH") for a in ZAVRSNI_TOKOVI)

    veze = [
        {
            "izvor": izvor,
            "cilj": cilj,
            "broj_iteracija": brojaci_veza[(izvor, cilj)],
            "indeks_kriticnosti": brojaci_veza[(izvor, cilj)] / broj_iteracija,
        }
        for izvor, cilj in parovi
    ]

    aktivnosti.sort(key=lambda r: r["indeks_kriticnosti"], reverse=True)
    veze.sort(key=lambda r: r["indeks_kriticnosti"], reverse=True)
    return {"aktivnosti": aktivnosti, "veze": veze}


def izvedi_s1(broj_iteracija=BROJ_ITERACIJA, sjeme=SJEME):
    provjeri_parametre_rizika()
    brojaci_aktivnosti, brojaci_veza = Counter(), Counter()
    retci, zavrsetci = simuliraj_zavrsetke(
        broj_iteracija, sjeme, spremi_retke=True,
        brojaci_aktivnosti=brojaci_aktivnosti, brojaci_veza=brojaci_veza,
    )
    return (
        retci,
        izracunaj_rezultate(zavrsetci, broj_iteracija, sjeme),
        zavrsetci,
        pripremi_indeks_kriticnosti(brojaci_aktivnosti, brojaci_veza, broj_iteracija),
    )


def rangiraj_rizike(puni_rezultati, broj_iteracija=BROJ_ITERACIJA, sjeme=SJEME):
    rang = []
    for rizik in RIZICI:
        if not rizik["ukljucen"] or rizik["vrsta"] != "Prijetnja":
            continue

        _, bez_rizika = simuliraj_zavrsetke(
            broj_iteracija, sjeme, izostavljeni_rizik=rizik["id"]
        )
        p80_bez = float(np.percentile(bez_rizika, 80))
        p_rok_bez = float(np.mean(bez_rizika <= ROK_PROJEKTA))
        rang.append({
            "rizik": rizik["id"],
            "naziv": rizik["naziv"],
            "p80_bez_rizika": p80_bez,
            "doprinos_p80": max(0.0, puni_rezultati["p80"] - p80_bez),
            "vjerojatnost_u_roku_bez_rizika": p_rok_bez,
            "poboljsanje_vjerojatnosti_u_roku": max(
                0.0, p_rok_bez - puni_rezultati["vjerojatnost_zavrsetka_u_roku"]
            ),
        })

    return sorted(rang, key=lambda r: r["doprinos_p80"], reverse=True)


def analiziraj_priliku(zavrsetci_s_prilikom, id_prilike="P1", broj_iteracija=BROJ_ITERACIJA, sjeme=SJEME):
    _, bez_prilike = simuliraj_zavrsetke(
        broj_iteracija, sjeme, izostavljeni_rizik=id_prilike
    )

    def ishodi(zavrsetci, naziv):
        tol = 1e-9
        return {
            "scenarij": naziv,
            "prije_roka": float(np.mean(zavrsetci < ROK_PROJEKTA - tol)),
            "tocno_na_roku": float(np.mean(np.isclose(zavrsetci, ROK_PROJEKTA, atol=tol, rtol=0))),
            "nakon_roka": float(np.mean(zavrsetci > ROK_PROJEKTA + tol)),
            "prosjecni_zavrsetak": float(np.mean(zavrsetci)),
            "p80": float(np.percentile(zavrsetci, 80)),
            "vjerojatnost_u_roku": float(np.mean(zavrsetci <= ROK_PROJEKTA)),
        }

    return [
        ishodi(bez_prilike, f"Bez prilike {id_prilike}"),
        ishodi(zavrsetci_s_prilikom, f"S prilikom {id_prilike}"),
    ]


def izracunaj_konvergenciju(zavrsetci, sjeme=SJEME):
    velicine = sorted({
        n for n in (500, 1000, 2500, 5000, 10000, 25000, 50000, len(zavrsetci))
        if n <= len(zavrsetci)
    })
    retci = []

    for n in velicine:
        uzorak = zavrsetci[:n]
        sd = float(np.std(uzorak, ddof=1 if n > 1 else 0))
        p50, p80, p90 = np.percentile(uzorak, [50, 80, 90])
        retci.append({
            "broj_iteracija": n,
            "sjeme": sjeme,
            "prosjecni_zavrsetak": float(np.mean(uzorak)),
            "p50": float(p50), "p80": float(p80), "p90": float(p90),
            "vjerojatnost_zavrsetka_u_roku": float(np.mean(uzorak <= ROK_PROJEKTA)),
            "standardna_devijacija": sd,
            "standardna_pogreska_prosjeka": float(sd / np.sqrt(n)),
        })

    return retci


def pripremi_ulaze_s1():
    retci = []
    for rizik in RIZICI:
        for i, ucinak in enumerate(ucinci_rizika(rizik)):
            retci.append({
                "id": rizik["id"], "vrsta": rizik["vrsta"], "naziv": rizik["naziv"],
                "tip_ucinka": "glavni" if i == 0 else "dodatni",
                "kvalitativna_vjerojatnost": rizik["kvalitativna_vjerojatnost"],
                "kvalitativni_utjecaj": rizik["kvalitativni_utjecaj"],
                "vjerojatnost": rizik["vjerojatnost"], "cilj": ucinak["cilj"],
                "minimum": ucinak["minimum"], "najvjerojatnije": ucinak["najvjerojatnije"],
                "maksimum": ucinak["maksimum"], "ukljucen": rizik["ukljucen"],
                "obrazlozenje": rizik["obrazlozenje"],
            })
    return retci


def spremi_s1(retci, rezultati, zavrsetci, rang, kriticnost, konvergencija, prilika):
    izlaz = mapa_izlaza()
    putanje = {
        "iteracije": izlaz / "s1_iteracije.csv",
        "sazetak": izlaz / "s1_sazetak.csv",
        "ulazi": izlaz / "s1_ulazi_rizika.csv",
        "rang": izlaz / "s1_rang_rizika.csv",
        "kriticnost_aktivnosti": izlaz / "s1_indeks_kriticnosti_aktivnosti.csv",
        "kriticnost_veza": izlaz / "s1_indeks_kriticnosti_veza.csv",
        "konvergencija": izlaz / "s1_konvergencija.csv",
        "podaci_prilike": izlaz / "s1_analiza_prilike_p1.csv",
        "histogram": izlaz / "s1_histogram.png",
        "s_krivulja": izlaz / "s1_s_krivulja.png",
        "tornado": izlaz / "s1_tornado_rizika.png",
        "utjecaj_na_rok": izlaz / "s1_utjecaj_prijetnji_na_rok.png",
        "graf_kriticnosti": izlaz / "s1_indeks_kriticnosti_mreze.png",
        "analiza_prilike": izlaz / "s1_analiza_prilike_p1.png",
        "graf_konvergencije": izlaz / "s1_konvergencija.png",
    }

    spremi_csv(putanje["iteracije"], retci)
    spremi_csv(putanje["sazetak"], [{"pokazatelj": k, "vrijednost": v} for k, v in rezultati.items()])
    spremi_csv(putanje["ulazi"], pripremi_ulaze_s1())
    spremi_csv(putanje["rang"], rang)
    spremi_csv(putanje["kriticnost_aktivnosti"], kriticnost["aktivnosti"])
    spremi_csv(putanje["kriticnost_veza"], kriticnost["veze"])
    spremi_csv(putanje["konvergencija"], konvergencija)
    spremi_csv(putanje["podaci_prilike"], prilika)

    nacrtaj_histogram(zavrsetci, rezultati, putanje["histogram"])
    nacrtaj_s_krivulju(zavrsetci, rezultati, putanje["s_krivulja"])
    nacrtaj_tornado(rang, putanje["tornado"])
    nacrtaj_utjecaj_na_rok(rang, putanje["utjecaj_na_rok"])
    nacrtaj_analizu_prilike(prilika, putanje["analiza_prilike"])
    nacrtaj_indeks_kriticnosti(kriticnost, putanje["graf_kriticnosti"])
    nacrtaj_konvergenciju(konvergencija, putanje["graf_konvergencije"])
    return putanje


def pokreni_s1():
    retci, rezultati, zavrsetci, kriticnost = izvedi_s1()
    rang = rangiraj_rizike(rezultati, rezultati["broj_iteracija"], rezultati["sjeme"])
    konvergencija = izracunaj_konvergenciju(zavrsetci, rezultati["sjeme"])
    prilika = analiziraj_priliku(
        zavrsetci, broj_iteracija=rezultati["broj_iteracija"], sjeme=rezultati["sjeme"]
    )
    putanje = spremi_s1(retci, rezultati, zavrsetci, rang, kriticnost, konvergencija, prilika)
    najkriticnija = kriticnost["aktivnosti"][0]

    print("\nPrije odgovora na rizike")
    print(f"Broj iteracija: {rezultati['broj_iteracija']}")
    print(f"Prosječni završetak: M{rezultati['prosjecni_zavrsetak']:.2f}")
    print(f"Najkasniji završetak: M{rezultati['najkasniji_zavrsetak']:.2f}")
    print(f"Standardna devijacija: {rezultati['standardna_devijacija']:.2f}")
    print(f"Standardna pogreška prosjeka: {rezultati['standardna_pogreska_prosjeka']:.4f}")
    print(f"P50 / P80 / P90: M{rezultati['p50']:.2f} / M{rezultati['p80']:.2f} / M{rezultati['p90']:.2f}")
    print(f"Vjerojatnost završetka do M{ROK_PROJEKTA:g}: {rezultati['vjerojatnost_zavrsetka_u_roku']:.1%}")
    print(f"Vjerojatnost kašnjenja: {rezultati['vjerojatnost_kasnjenja']:.1%}")
    print(f"Očekivano kašnjenje: {rezultati['ocekivano_kasnjenje']:.2f} mjeseci")
    print(f"Potrebna P80 rezerva: {rezultati['potrebna_rezerva_p80']:.2f} mjeseci")
    print(f"Najutjecajniji rizik prema P80: {rang[0]['rizik']}")
    print(f"Najveći CPM indeks kritičnosti: {najkriticnija['aktivnost']} ({najkriticnija['indeks_kriticnosti']:.1%})")
    print(f"Rezultati: {putanje['iteracije'].parent}")
