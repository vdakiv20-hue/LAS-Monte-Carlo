"""Zajednički statistički pokazatelji Monte Carlo simulacije."""

import numpy as np

from src.konfiguracija import ROK_PROJEKTA


def izracunaj_rezultate(zavrsetci, broj_iteracija, sjeme):
    sd = float(np.std(zavrsetci, ddof=1 if broj_iteracija > 1 else 0))
    p50, p80, p90 = (float(x) for x in np.percentile(zavrsetci, [50, 80, 90]))
    kasnjenja = np.maximum(zavrsetci - ROK_PROJEKTA, 0)

    return {
        "broj_iteracija": broj_iteracija,
        "sjeme": sjeme,
        "rok": ROK_PROJEKTA,
        "prosjecni_zavrsetak": float(np.mean(zavrsetci)),
        "najraniji_zavrsetak": float(np.min(zavrsetci)),
        "najkasniji_zavrsetak": float(np.max(zavrsetci)),
        "varijanca": sd**2,
        "standardna_devijacija": sd,
        "standardna_pogreska_prosjeka": float(sd / np.sqrt(broj_iteracija)),
        "p50": p50,
        "p80": p80,
        "p90": p90,
        "vjerojatnost_zavrsetka_prije_roka": float(np.mean(zavrsetci < ROK_PROJEKTA)),
        "vjerojatnost_zavrsetka_u_roku": float(np.mean(zavrsetci <= ROK_PROJEKTA)),
        "vjerojatnost_kasnjenja": float(np.mean(zavrsetci > ROK_PROJEKTA)),
        "ocekivano_kasnjenje": float(np.mean(kasnjenja)),
        "potrebna_rezerva_p80": max(0.0, p80 - ROK_PROJEKTA),
    }
