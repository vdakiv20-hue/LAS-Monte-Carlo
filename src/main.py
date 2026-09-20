import sys


def main():
    scenarij = sys.argv[1].lower() if len(sys.argv) > 1 else "s0"

    if scenarij == "s0":
        from src.s0_osnovni_raspored import pokreni_s0

        pokreni_s0()
    elif scenarij == "s1":
        from src.s1_monte_carlo import pokreni_s1

        pokreni_s1()
    elif scenarij == "s2":
        from src.s2_monte_carlo import pokreni_s2

        pokreni_s2()
    else:
        raise ValueError("Dopušteni scenariji su s0, s1 i s2.")


if __name__ == "__main__":
    main()