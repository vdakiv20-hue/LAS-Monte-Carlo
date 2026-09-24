"""Grafički prikazi za scenarije S0, S1 i S2."""

import matplotlib
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.ticker import PercentFormatter

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.konfiguracija import ROK_PROJEKTA

# Postavke grafičkog prikaza mreže.
KRATKI_NAZIVI = {
    "A1.1": "Analiza HE okvira",
    "A1.2": "Analiza potreba poduzeća",
    "A2.1": "Razvoj koncepta",
    "A3.1": "Razvoj prototipa",
    "A3.2": "Testiranje i validacija",
    "A4.1": "Primjeri uporabe",
    "A5.1": "Suradnja i komercijalizacija",
    "A5.2": "Diseminacija i umrežavanje",
}

# Stabilne pozicije za S0 i S1 mrežni dijagram.
POZICIJE = {
    "START": (0.7, 4.0),
    "A1.1": (3.0, 6.0),
    "A1.2": (3.0, 2.0),
    "A2.1": (6.2, 4.0),
    "A3.1": (9.2, 4.0),
    "A3.2": (12.2, 6.0),
    "A4.1": (12.2, 2.0),
    "A5.1": (15.6, 5.0),
    "A5.2": (15.6, 1.2),
    "FINISH": (19.0, 3.2),
}

# izvor, cilj, oznaka, pomak_x, pomak_y, zakrivljenost, položaj oznake
VEZE_CRTANJA = (
    ("START", "A1.1", "početak M2", -0.20, 0.18, 0.00, 0.35),
    ("START", "A1.2", "početak M3", -0.20, -0.18, 0.00, 0.35),
    ("A1.1", "A2.1", "FS-1", 0.00, 0.18, 0.00, 0.52),
    ("A1.2", "A2.1", "FS-2", 0.00, -0.18, 0.00, 0.52),
    ("A2.1", "A3.1", "FS", 0.00, 0.27, 0.00, 0.50),
    ("A3.1", "A3.2", "FS-2 / FF+0", 0.00, 0.18, 0.00, 0.45),
    ("A3.1", "A4.1", "FF+0", 0.00, -0.18, 0.00, 0.50),
    ("A4.1", "A5.1", "FF+0", -0.05, 0.18, -0.05, 0.55),
    ("A3.2", "A5.2", "FF+0", 0.10, 0.08, 0.08, 0.25),
    ("A4.1", "A5.2", "FF+0", 0.05, -0.28, -0.04, 0.43),
    ("A5.1", "FINISH", "", 0.00, 0.10, -0.05, 0.58),
    ("A5.2", "FINISH", "", 0.00, -0.10, 0.05, 0.58),
)


def oznaka_veze(tip, pomak):
    """Vraća kratku oznaku veze, npr. FS-2 ili FF+0."""
    if pomak == 0:
        return tip
    znak = "+" if pomak > 0 else ""
    return f"{tip}{znak}{pomak:g}"


def _spremi(putanja, dpi=170):
    plt.tight_layout()
    plt.savefig(putanja, dpi=dpi, bbox_inches="tight")
    plt.close()


def _cvor(ax, oznaka, tekst, rub="#5B7FA3", pozadina="#EAF2FA", debljina=1.6,
          sirina=2.55, visina=1.25):
    x, y = POZICIJE[oznaka]
    ax.add_patch(Rectangle(
        (x - sirina / 2, y - visina / 2), sirina, visina,
        facecolor=pozadina, edgecolor=rub, linewidth=debljina, zorder=2,
    ))
    ax.text(x, y, tekst, ha="center", va="center", fontsize=10,
            linespacing=1.25, zorder=3)


def _strelica(ax, izvor, cilj, oznaka, dx, dy, rad, label_t,
              boja="#667085", debljina=1.7, dodatni_tekst=""):
    x1, y1 = POZICIJE[izvor]
    x2, y2 = POZICIJE[cilj]
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops={
            "arrowstyle": "-|>", "color": boja, "lw": debljina,
            "shrinkA": 32, "shrinkB": 32, "mutation_scale": 17,
            "connectionstyle": f"arc3,rad={rad}",
        },
        zorder=1,
    )

    smjer = f"{'POČETAK' if izvor == 'START' else izvor} → {cilj}"
    tekst = smjer + (f"\n{oznaka}" if oznaka else "") + dodatni_tekst
    ax.text(
        x1 + (x2 - x1) * label_t + dx,
        y1 + (y2 - y1) * label_t + dy,
        tekst,
        fontsize=8.7, fontweight="semibold", ha="center", va="center",
        linespacing=1.15,
        bbox={
            "facecolor": "white", "edgecolor": "#D0D5DD", "linewidth": 0.7,
            "alpha": 0.97, "boxstyle": "round,pad=0.22",
        },
        zorder=5,
    )


def nacrtaj_s0_mrezu(raspored, cpm, putanja):
    fig, ax = plt.subplots(figsize=(20, 9))

    _cvor(ax, "START", "POČETAK", rub="#6B7280", pozadina="#F3F4F6",
          sirina=1.75, visina=0.95)

    for oznaka, naziv in KRATKI_NAZIVI.items():
        aktivnost = raspored[oznaka]
        tf = cpm["aktivnosti"][oznaka]["ukupna_rezerva"]
        tekst = (
            f"{oznaka}\n{naziv}\n"
            f"M{aktivnost['pocetak']:g}-M{aktivnost['zavrsetak']:g}\n"
            f"T = {aktivnost['trajanje']:g} mj. | TF = {tf:g} mj."
        )
        _cvor(ax, oznaka, tekst)

    _cvor(
        ax, "FINISH", f"FINISH\nM{raspored['FINISH']['zavrsetak']:g}",
        rub="#6B7280", pozadina="#F3F4F6", sirina=2.0, visina=1.0,
    )

    for veza in VEZE_CRTANJA:
        _strelica(ax, *veza)

    ax.set_title("S0 - PDM mrežni dijagram projektnih aktivnosti", fontsize=16, pad=18)
    ax.text(
        0.01, 0.02,
        "T = trajanje aktivnosti | TF = ukupna vremenska rezerva prema CPM/PDM izračunu\n"
        "A6.1-A6.3 nisu prikazane jer prate stvarni završetak cijelog projekta.",
        transform=ax.transAxes, fontsize=10, va="bottom",
    )
    ax.set_xlim(-0.7, 20.4)
    ax.set_ylim(0.1, 7.1)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(putanja, dpi=200, bbox_inches="tight")
    plt.close(fig)


def nacrtaj_histogram(zavrsetci, sazetak, putanja):

    p80 = f"{sazetak['p80']:.1f}".replace(".", ",")
    prosjek = sazetak["prosjecni_zavrsetak"]
    sd = sazetak["standardna_devijacija"]

    prosjek_oznaka = f"{prosjek:.2f}".replace(".", ",")
    donja_sd = prosjek - sd
    gornja_sd = prosjek + sd

    donja_sd_oznaka = f"{donja_sd:.2f}".replace(".", ",")
    gornja_sd_oznaka = f"{gornja_sd:.2f}".replace(".", ",")

    plt.figure(figsize=(10, 5.5))

    plt.hist(
        zavrsetci,
        bins=35,
        color="#4C78A8",
        edgecolor="white"
    )

    # Raspon jedne standardne devijacije oko prosjeka
    plt.axvspan(
        donja_sd,
        gornja_sd,
        color="#59A14F",
        alpha=0.12,
        label=f"Prosjek ± 1 SD = M{donja_sd_oznaka} – M{gornja_sd_oznaka}"
    )

    # Planirani rok
    plt.axvline(
        ROK_PROJEKTA,
        color="#D62728",
        linestyle="--",
        label=f"Planirani rok = M{ROK_PROJEKTA:g}"
    )

    # Prosječni završetak
    plt.axvline(
        prosjek,
        color="#59A14F",
        linestyle="-.",
        linewidth=2,
        label=f"Prosjek = M{prosjek_oznaka}"
    )

    # P80
    plt.axvline(
        sazetak["p80"],
        color="#F59E0B",
        label=f"P80 = M{p80} (80 % scenarija završava do tog mjeseca)"
    )

    plt.title("S1 - distribucija simuliranog završetka projekta")
    plt.xlabel("Simulirani završetak projekta (mjesec)")
    plt.ylabel("Broj simuliranih scenarija")

    plt.legend()

    _spremi(putanja)


def nacrtaj_s_krivulju(zavrsetci, sazetak, putanja):
    sortirani = np.sort(zavrsetci)
    y = np.arange(1, len(sortirani) + 1) / len(sortirani)

    plt.figure(figsize=(11, 6))
    plt.plot(
        sortirani, y,
        linewidth=2.5,
        label="Kumulativna vjerojatnost završetka"
    )

    # Vjerojatnost završetka za odabrane rokove M36–M40
    rokovi = [ROK_PROJEKTA + i for i in range(5)]

    for rok in rokovi:
        p = float(np.mean(zavrsetci <= rok))

        if rok == ROK_PROJEKTA:
            boja = "#D62728"
            stil = "--"
        else:
            boja = "#4C78A8"
            stil = ":"

        plt.vlines(
            rok, 0, p,
            colors=boja,
            linestyles=stil,
            linewidth=1.5
        )
        plt.scatter(rok, p, color=boja, zorder=5)

        plt.annotate(
        f"M{rok:g}\n{p:.1%}".replace(".", ","),
        (rok, p),
        xytext=(17, -12),
        textcoords="offset points",
        ha="center",
        va="top",
        fontsize=9,
        bbox={
            "boxstyle": "round,pad=0.3",
            "facecolor": "white",
            "edgecolor": "none",
            "alpha": 0.7
        }
)

    plt.title("S1 - kumulativna vjerojatnost završetka projekta")
    plt.xlabel("Mjesec do kojeg projekt završava")
    plt.ylabel("Udio simuliranih scenarija završenih do tog mjeseca")
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))
    plt.ylim(0, 1)
    plt.grid(alpha=0.15, linestyle="--")
    plt.legend(loc="lower right")

    _spremi(putanja)


def _rang_prijetnji(rang, putanja, kljuc, naslov, x_oznaka, boja, faktor=1.0, format_vrijednosti=None):
    podaci = sorted(rang, key=lambda r: r[kljuc], reverse=True)
    oznake = [f"{r['rizik']} - {r['naziv']}" for r in podaci]
    vrijednosti = [r[kljuc] * faktor for r in podaci]
    format_vrijednosti = format_vrijednosti or (lambda x: f"{x:.2f}")

    plt.figure(figsize=(12, 6))
    stupci = plt.barh(oznake, vrijednosti, color=boja)
    plt.gca().invert_yaxis()
    plt.bar_label(stupci, labels=[format_vrijednosti(v) for v in vrijednosti], padding=3)
    plt.title(naslov)
    plt.xlabel(x_oznaka)
    plt.ylabel("Projektna prijetnja")
    plt.grid(axis="x", alpha=0.20, linestyle="--")
    _spremi(putanja)


def nacrtaj_tornado(rang, putanja):
    def oznaka(v):
        return "<0,01 mj." if abs(v) < 0.005 else f"{v:.2f}".replace(".", ",") + " mj."

    _rang_prijetnji(
        rang, putanja, "doprinos_p80",
        "Utjecaj pojedinih prijetnji na P80 završetka projekta",
        "Smanjenje P80 nakon uklanjanja prijetnje (mjeseci)",
        "#E45756", format_vrijednosti=oznaka,
    )


def nacrtaj_utjecaj_na_rok(rang, putanja):
    _rang_prijetnji(
        rang, putanja, "poboljsanje_vjerojatnosti_u_roku",
        "Utjecaj pojedinih prijetnji na završetak projekta u roku",
        f"Povećanje vjerojatnosti završetka do M{ROK_PROJEKTA:g} nakon uklanjanja prijetnje (postotni bodovi)",
        "#4E79A7", faktor=100,
        format_vrijednosti=lambda x: f"{x:.2f}".replace(".", ",") + " p. b.",
    )


def nacrtaj_analizu_prilike(analiza, putanja):
    scenariji = [r["scenarij"] for r in analiza]
    prije = np.array([r["prije_roka"] for r in analiza])
    tocno = np.array([r["tocno_na_roku"] for r in analiza])
    nakon = np.array([r["nakon_roka"] for r in analiza])
    rok = f"M{ROK_PROJEKTA:g}"

    plt.figure(figsize=(9, 6))
    plt.bar(scenariji, prije, label=f"Završetak prije {rok}", color="#59A14F")
    plt.bar(scenariji, tocno, bottom=prije, label=f"Završetak točno u {rok}", color="#F2CF5B")
    plt.bar(scenariji, nakon, bottom=prije + tocno, label=f"Završetak nakon {rok}", color="#E15759")

    for i in range(len(scenariji)):
        for vrijednost, pocetak in zip(
            (prije[i], tocno[i], nakon[i]),
            (0, prije[i], prije[i] + tocno[i]),
        ):
            if vrijednost >= 0.03:
                plt.text(i, pocetak + vrijednost / 2,
                         f"{vrijednost:.1%}".replace(".", ","),
                         ha="center", va="center", fontsize=10)

    plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))
    plt.ylim(0, 1)
    plt.title("Utjecaj prilike P1 na ostvarenje planiranog roka")
    plt.xlabel("Scenarij")
    plt.ylabel("Udio simuliranih scenarija")
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)
    _spremi(putanja)


def nacrtaj_konvergenciju(konvergencija, putanja):
    x = [r["broj_iteracija"] for r in konvergencija]
    prosjek = [r["prosjecni_zavrsetak"] for r in konvergencija]
    p80 = [r["p80"] for r in konvergencija]

    plt.figure(figsize=(10, 5.5))
    plt.plot(x, prosjek, marker="o", linewidth=2, label="Prosječni završetak")
    plt.plot(x, p80, marker="o", linewidth=2, label="P80")
    plt.xscale("log")
    plt.xticks(x, [f"{n:,}".replace(",", ".") for n in x], rotation=30)

    for vrijednosti, pomak in ((prosjek, -10), (p80, 10)):
        plt.annotate(
            f"M{vrijednosti[-1]:.2f}".replace(".", ","),
            (x[-1], vrijednosti[-1]), xytext=(-8, pomak),
            textcoords="offset points", ha="right", fontsize=9,
        )

    plt.title("Stabilnost procjena s povećanjem broja Monte Carlo iteracija")
    plt.xlabel("Broj simulacijskih iteracija")
    plt.ylabel("Procijenjeni mjesec završetka projekta")
    plt.grid(alpha=0.25, linestyle="--")
    plt.legend()
    _spremi(putanja)


def nacrtaj_indeks_kriticnosti(indeks, putanja):
    ik_a = {r["aktivnost"]: r["indeks_kriticnosti"] for r in indeks["aktivnosti"]}
    ik_v = {(r["izvor"], r["cilj"]): r["indeks_kriticnosti"] for r in indeks["veze"]}
    fig, ax = plt.subplots(figsize=(20, 9))

    _cvor(ax, "START", "POČETAK", rub="#6B7280", pozadina="#F3F4F6",
          sirina=1.75, visina=0.95)

    for oznaka, naziv in KRATKI_NAZIVI.items():
        vrijednost = ik_a.get(oznaka, 0.0)
        aktivna = vrijednost >= 0.01
        _cvor(
            ax, oznaka,
            f"{oznaka}\n{naziv}\nIK = {vrijednost:.1%}".replace(".", ","),
            rub="#C62828" if aktivna else "#5B7FA3",
            pozadina="#FDEBEC" if aktivna else "#EAF2FA",
            debljina=1.5 + 2.5 * vrijednost if aktivna else 1.5,
        )

    _cvor(ax, "FINISH", "FINISH", rub="#6B7280", pozadina="#F3F4F6",
          sirina=2.0, visina=1.0)

    for izvor, cilj, tip, dx, dy, rad, label_t in VEZE_CRTANJA:
        vrijednost = 0.0 if izvor == "START" else ik_v.get((izvor, cilj), 0.0)
        aktivna = vrijednost >= 0.01
        dodatak = "" if vrijednost < 0.001 else f"\nIK = {vrijednost:.1%}".replace(".", ",")
        _strelica(
            ax, izvor, cilj, tip, dx, dy, rad, label_t,
            boja="#C62828" if aktivna else "#98A2B3",
            debljina=1.5 + 4.0 * vrijednost if aktivna else 1.25,
            dodatni_tekst=dodatak,
        )

    ax.set_title("S1 - CPM indeks kritičnosti aktivnosti i mrežnih veza", fontsize=16, pad=18)
    ax.text(
        0.01, 0.02,
        "IK = udio Monte Carlo iteracija u kojima aktivnost ima ukupnu vremensku rezervu TF = 0.\n"
        "Veza se smatra kritičnom kada je aktivna bez slaka i povezuje kritične aktivnosti. "
        "Rizici s više ciljeva, uključujući T8, mogu mijenjati kritičnost više aktivnosti u istoj iteraciji.",
        transform=ax.transAxes, fontsize=10, va="bottom",
    )
    ax.set_xlim(-0.7, 20.4)
    ax.set_ylim(0.1, 7.1)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(putanja, dpi=200, bbox_inches="tight")
    plt.close(fig)
    

def nacrtaj_usporedbu_s_krivulja(
    zavrsetci_s1, zavrsetci_s2, s1, s2, putanja
):
    plt.figure(figsize=(11, 6))

    boja_s1 = "#4C78A8"
    boja_s2 = "#59A14F"

    # S1
    sortirani_s1 = np.sort(zavrsetci_s1)
    y_s1 = np.arange(1, len(sortirani_s1) + 1) / len(sortirani_s1)

    plt.plot(
        sortirani_s1,
        y_s1,
        linewidth=2.3,
        color=boja_s1,
        label="S1 - prije odgovora"
    )

    # S2
    sortirani_s2 = np.sort(zavrsetci_s2)
    y_s2 = np.arange(1, len(sortirani_s2) + 1) / len(sortirani_s2)

    plt.plot(
        sortirani_s2,
        y_s2,
        linewidth=2.3,
        color=boja_s2,
        label="S2 - nakon odgovora"
    )

    # Odabrani rokovi za usporedbu
    rokovi = [ROK_PROJEKTA + i for i in range(5)]

    for rok in rokovi:
        p_s1 = float(np.mean(zavrsetci_s1 <= rok))
        p_s2 = float(np.mean(zavrsetci_s2 <= rok))

        plt.scatter(rok, p_s1, color=boja_s1, zorder=5)
        plt.scatter(rok, p_s2, color=boja_s2, zorder=5)

        # Ručni pomaci labela: (x, y, ha, va)
        pomaci_s1 = {
            36: (6, -8, "left", "top"),
            37: (4, -6, "left", "top"),
            38: (4, -4, "left", "top"),
            39: (6, -6, "left", "top"),
            40: (8, -2, "left", "top"),
        }

        pomaci_s2 = {
            36: (7, 6, "left", "bottom"),
            37: (9, 3, "left", "bottom"),
            38: (3, -9, "left", "top"),
            39: (18, -9, "right", "top"),
            40: (-39, -8, "left", "top"),
        }

        dx1, dy1, ha1, va1 = pomaci_s1[rok]
        plt.annotate(
            f"S1 {p_s1:.1%}".replace(".", ","),
            (rok, p_s1),
            xytext=(dx1, dy1),
            textcoords="offset points",
            ha=ha1,
            va=va1,
            fontsize=8.5,
            color=boja_s1,
        )

        dx2, dy2, ha2, va2 = pomaci_s2[rok]
        plt.annotate(
            f"S2 {p_s2:.1%}".replace(".", ","),
            (rok, p_s2),
            xytext=(dx2, dy2),
            textcoords="offset points",
            ha=ha2,
            va=va2,
            fontsize=8.5,
            color=boja_s2,
        )

    # Planirani rok
    plt.axvline(
        ROK_PROJEKTA,
        color="#D62728",
        linestyle="--",
        linewidth=1.5,
        label=f"Planirani rok = M{ROK_PROJEKTA:g}"
    )

    plt.gca().yaxis.set_major_formatter(PercentFormatter(1.0))
    plt.ylim(0, 1)

    plt.title(
        "Učinak odgovora na rizike na vjerojatnost završetka projekta"
    )
    plt.xlabel("Mjesec do kojeg projekt završava")
    plt.ylabel(
        "Udio simuliranih scenarija završenih do tog mjeseca"
    )

    plt.grid(alpha=0.15, linestyle="--")
    plt.legend(loc="lower right")

    _spremi(putanja)


def nacrtaj_usporedbu_pokazatelja(s1, s2, putanja):
    oznake = ["Prosjek", "P50", "P80", "P90"]
    kljucevi = ["prosjecni_zavrsetak", "p50", "p80", "p90"]
    v1 = np.array([s1[k] for k in kljucevi])
    v2 = np.array([s2[k] for k in kljucevi])
    y = np.arange(len(oznake))

    plt.figure(figsize=(10, 5.5))
    for i in range(len(oznake)):
        plt.plot([v1[i], v2[i]], [y[i], y[i]], color="#B8BDC5", linewidth=2)
    plt.scatter(v1, y, s=85, color="#4C78A8", label="S1 - prije odgovora")
    plt.scatter(v2, y, s=85, color="#59A14F", label="S2 - nakon odgovora")

    for i in range(len(oznake)):
        plt.text(v1[i], y[i] + 0.18, f"M{v1[i]:.2f}".replace(".", ","), ha="center", fontsize=9)
        plt.text(v2[i], y[i] - 0.18, f"M{v2[i]:.2f}".replace(".", ","), ha="center", fontsize=9)

    plt.yticks(y, oznake)
    plt.gca().invert_yaxis()
    plt.title("Promjena ključnih pokazatelja nakon odgovora na rizike")
    plt.xlabel("Mjesec završetka projekta")
    plt.grid(axis="x", alpha=0.20, linestyle="--")
    plt.legend()
    _spremi(putanja)
