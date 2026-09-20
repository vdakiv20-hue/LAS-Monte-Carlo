# LAS – Monte Carlo analiza projektnih rizika

Projekt prikazuje primjenu Monte Carlo metode na vremenski raspored projekta LAS. Model je organiziran u tri scenarija:

- **S0** – deterministički osnovni raspored bez utjecaja modeliranih rizika;
- **S1** – Monte Carlo simulacija s modeliranim rizicima prije odgovora na rizike;
- **S2** – Monte Carlo simulacija nakon primjene pretpostavljenih odgovora na rizike.

## Struktura koda

| Datoteka | Uloga |
|---|---|
| `src/konfiguracija.py` | osnovni projektni podatci, planirana trajanja, najraniji počeci aktivnosti i mrežne veze |
| `src/mrezni_model.py` | izračun rasporeda, vremenskih rezervi i kritičnosti aktivnosti i mrežnih veza |
| `src/rizici.py` | prijetnje, prilika, vjerojatnosti i trokutasti vremenski učinci |
| `src/odgovori_na_rizike.py` | pretpostavljene mjere odgovora i prilagodba parametara rizika za scenarij S2 |
| `src/grafovi.py` | grafički prikazi rezultata za scenarije S0, S1 i S2 |
| `src/izvjestaj.py` | ispis i spremanje rezultata |
| `src/simulacija.py` | zajedničke funkcije za izračun statističkih pokazatelja Monte Carlo rezultata |
| `src/s0_osnovni_raspored.py` | scenarij S0, kontrolne provjere i prikaz osnovne projektne mreže |
| `src/s1_monte_carlo.py` | scenarij S1, analiza rizika, prilike, kritičnosti i konvergencije |
| `src/s2_monte_carlo.py` | scenarij S2, usporedba S1 i S2 te analiza osjetljivosti |
| `src/main.py` | pokretanje odabranog scenarija |

## Instalacija

Potrebne biblioteke instaliraju se naredbom:

```bash
pip install -r requirements.txt


## Pokretanje

Iz glavne mape projekta:

```bash
python -m src.main s0
python -m src.main s1
python -m src.main s2
```

## Mrežna logika

Model koristi PDM veze s planiranim najranijim počecima iz Gantta. Glavne veze su:

- A1.1 → A2.1: **FS−1**
- A1.2 → A2.1: **FS−2**
- A2.1 → A3.1: **FS**
- A3.1 → A3.2: **FS−2 i FF+0**
- A3.1 → A4.1: **FF+0**
- A4.1 → A5.1: **FF+0**
- A3.2 → A5.2: **FF+0**
- A4.1 → A5.2: **FF+0**

Završetak sadržajne mreže određuje kasniji završetak aktivnosti **A5.1 ili A5.2**. Rizici, uključujući koordinacijski T8, djeluju preko trajanja zahvaćenih aktivnosti, nakon čega mreža sama prenosi njihov učinak do završetka projekta.


## CPM i indeks kritičnosti

S0 koristi formalni PDM/CPM backward pass. Za svaku aktivnost računaju se najraniji i najkasniji termini te **ukupna vremenska rezerva (total float, TF)**. Aktivnost je kritična kada je `TF = 0`.

U S1 se nakon svake Monte Carlo iteracije ponovno računa CPM nad simuliranim trajanjem aktivnosti. **Indeks kritičnosti (IK)** je udio iteracija u kojima aktivnost ima `TF = 0`. Mrežna veza je kritična kada je bez slaka i povezuje kritične aktivnosti.

Indeks kritičnosti računa se za aktivnosti i mrežne veze, ne za same rizike. T8 zato nema zasebnu IK vrijednost, ali budući da djeluje na više aktivnosti, može mijenjati njihove rezerve, kritičnost i završni put u pojedinoj simulacijskoj iteraciji.

## Glavni izlazi

### S0

- `s0_raspored.csv`
- `s0_mrezni_dijagram.png`

### S1

-`s1_sazetak.csv`
-`s1_ulazi_rizika.csv`
-`s1_iteracije.csv`
-`s1_rang_rizika.csv`
-`s1_indeks_kriticnosti_aktivnosti.csv`
-`s1_indeks_kriticnosti_veza.csv`
-`s1_konvergencija.csv`
-`s1_analiza_prilike_p1.csv`
-`s1_histogram.png`
-`s1_s_krivulja.png`
-`s1_tornado_rizika.png`
-`s1_utjecaj_prijetnji_na_rok.png`
-`s1_indeks_kriticnosti_mreze.png`
-`s1_analiza_prilike_p1.png`
-`s1_konvergencija.png`

### S2

- `s2_sazetak.csv`
- `s2_ulazi_i_mjere.csv`
- `usporedba_s1_s2.csv`
- `s2_osjetljivost_faktora.csv` (20.000 iteracija po faktoru 0,60 / 0,70 / 0,80)
- `usporedba_s1_s2_s_krivulje.png`
- `usporedba_s1_s2_pokazatelji.png`
