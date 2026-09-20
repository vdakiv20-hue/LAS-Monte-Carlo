"""Mjere odgovora i demonstracijski faktori za scenarij S2."""

FAKTOR_PREOSTALE_VJEROJATNOSTI = 0.70
FAKTOR_PREOSTALOG_UCINKA = 0.70
FAKTOR_POVECANJA_VJEROJATNOSTI_PRILIKE = 1.30

MJERE_MITIGACIJE = {
    "T1": "Više kanala za uključivanje dionika, raniji pozivi i kombiniranje kvantitativnih i kvalitativnih metoda.",
    "T2": "Radionice zajedničkog oblikovanja, iterativna provjera zahtjeva i rana validacija koncepta.",
    "T3": "Rana provjera kvalitete i formata podataka, standardizacija, integracijsko testiranje i zamjenski scenariji djelomične integracije.",
    "T4": "Rano uključivanje pilot-korisnika, edukacija, tehnička podrška i iterativno testiranje korisničkog iskustva.",
    "T5": "Jasni kriteriji performansi, ponovno treniranje i prilagodba modela, objašnjiva AI, ljudski nadzor te dodatna evaluacija i validacija.",
    "T6": "Paralelna priprema publikacija i prijava, više ciljnih kanala te ranije planiranje rokova diseminacije.",
    "T7": "Rana analiza tržišta i konkurencije, uključivanje partnerskih mreža i iterativna prilagodba poslovnog modela.",
    "T8": "Redoviti koordinacijski sastanci, praćenje odluka, jasne odgovornosti i pravodobna eskalacija zastoja.",
    "T9": "Modularni dizajn, rano testiranje opterećenja i interoperabilnosti te plan skaliranja prije završne validacije.",
}

MJERE_POBOLJSANJA_PRILIKA = {
    "P1": "Aktivno i ranije uključivanje partnera te pravodobno dijeljenje tržišnih, stručnih i kontaktnih informacija.",
}


def provjeri_mjere_mitigacije(rizici):
    prijetnje = {r["id"] for r in rizici if r["vrsta"] == "Prijetnja" and r["ukljucen"]}
    if prijetnje != set(MJERE_MITIGACIJE):
        raise ValueError("Mjere mitigacije nisu usklađene s uključenim prijetnjama.")
    return True


def provjeri_odgovore_na_prilike(rizici):
    prilike = {r["id"] for r in rizici if r["vrsta"] == "Prilika" and r["ukljucen"]}
    if prilike != set(MJERE_POBOLJSANJA_PRILIKA):
        raise ValueError("Mjere poboljšanja nisu usklađene s uključenim prilikama.")
    return True
