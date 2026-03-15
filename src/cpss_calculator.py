"""
CPSS Calculator — Cyber-Physical Severity Scale
"""

import math
import argparse
import json

# Persistence factor P — estimated remediation duration
P_DAYS    = 1     # Days to weeks; complete natural recovery
P_MONTHS  = 10    # Months to one year (EPA SPCC oil spill guidance)
P_YEARS   = 100   # One to ten years (EPA CERCLA avg. cleanup ~7 years)
P_DECADES = 1000  # Decades or irreversible (IAEA post-accident decontamination)

# Default P by hazard category; use observed data when available
DEFAULT_PERSISTENCE = {
    "mechanical":   P_DAYS,
    "electrical":   P_DAYS,    # use P_MONTHS if PCB/transformer oil released
    "hydrological": P_MONTHS,
    "thermal":      P_MONTHS,  # use P_YEARS for hydrocarbon soil contamination
    "chemical":     P_YEARS,
    "radiological": P_DECADES,
    "none":         P_DAYS,
}


def human_score(deaths: int, hospitalized: int = 0) -> float:
    """H = log10(deaths * 100 + hospitalized * 10 + 1)
    H=4 ~ 100 deaths or ~1,000 hospitalized.
    Hospitalized weight (x10) reflects ~1/10 of fatality per DALY disability weights.
    Calibrated so 100 deaths == 10M service disruption (I=4).
    """
    return math.log10(deaths * 100 + hospitalized * 10 + 1)


def env_score(area_m2: float, persistence: int) -> float:
    """E = log10(area_m2 * P / 10); E=0 when no contamination release.
    E=2 ~ 100 m2 contaminated for months (building scale).
    E=4 ~ 10,000 m2 contaminated for months (local scale).
    E=6 ~ 1 km2 contaminated for years.
    Capped at 10.
    """
    if area_m2 <= 0:
        return 0.0
    return min(10.0, max(0.0, math.log10(area_m2 * persistence / 10)))


def infra_score(population: int) -> float:
    """I = log10(population / 1000 + 1)
    I=4 ~ 10M people. Calibrated relative to H: 100 deaths == 10M service disruption.
    """
    return math.log10(population / 1000 + 1)


def economic_score(loss_usd: float) -> float:
    """C = log10(loss_usd / 100000); loss = 0 -> C = 0
    C=3 ~ $100M, C=4 ~ $1B.
    Use direct confirmed loss only (exclude indirect/estimated losses).
    Losses below $100,000 USD yield a negative log value; these are clamped to 0.
    """
    if loss_usd <= 0:
        return 0.0
    return max(0.0, math.log10(loss_usd / 100000))


def cpss_class(score: float) -> str:
    if score == 0:
        return "NONE"
    elif score <= 2:
        return "LOW"
    elif score <= 4:
        return "MODERATE"
    elif score <= 6:
        return "SEVERE"
    elif score <= 8:
        return "CATASTROPHIC"
    else:
        return "CRITICAL"


def vector_string(h: float, e: float, i: float, c: float,
                  actual: float, potential: float = None) -> str:
    """Return CPSS vector string.
    Format: CPSS:1.0/H:<h>/E:<e>/I:<i>/C:<c>/A:<actual>[/P:<potential>]
    All dimension values rounded to one decimal place.
    """
    s = f"CPSS:1.0/H:{h:.1f}/E:{e:.1f}/I:{i:.1f}/C:{c:.1f}/A:{actual:.1f}"
    if potential is not None:
        s += f"/P:{potential:.1f}"
    return s


def assess(deaths: int = 0, hospitalized: int = 0,
           env_area_m2: float = 0, env_persistence: int = P_DAYS,
           population: int = 0, loss_usd: float = 0) -> dict:
    """
    Calculate CPSS score from raw impact values.

    Parameters
    ----------
    deaths          : number of fatalities
    hospitalized    : number of hospitalized (serious injuries)
    env_area_m2     : contaminated area in square metres
    env_persistence : persistence factor P (use module constants
                      P_DAYS / P_MONTHS / P_YEARS / P_DECADES)
    population      : number of people affected (infrastructure)
    loss_usd        : economic loss in USD

    Returns
    -------
    dict with H, E, I, C, CPSS, class
    """
    h = human_score(deaths, hospitalized)
    e = env_score(env_area_m2, env_persistence)
    i = infra_score(population)
    c = economic_score(loss_usd)
    score = max(h, e, i, c)

    return {
        "H": round(h, 2),
        "E": round(e, 2),
        "I": round(i, 2),
        "C": round(c, 2),
        "CPSS": round(score, 2),
        "class": cpss_class(score),
    }


def main():
    parser = argparse.ArgumentParser(
        description="CPSS — Cyber-Physical Severity Scale Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  # Chemical plant leak — hazard flag auto-sets P=100
  python3 cpss_calculator.py --hazard chemical --env-area 5000 \\
      --population 20000 --loss 80000000

  # With CPSS-Potential and calculation details
  python3 cpss_calculator.py --hazard chemical --env-area 5000 \\
      --population 20000 --loss 80000000 --potential 6.0 --explain

  # JSON output for tool integration
  python3 cpss_calculator.py --hazard hydrological --env-area 10000 \\
      --population 1000 --potential 5.0 --json
""",
    )
    parser.add_argument("--deaths", type=int, default=0,
                        help="Number of fatalities")
    parser.add_argument("--hospitalized", type=int, default=0,
                        help="Number of hospitalized (serious injuries)")
    parser.add_argument("--env-area", type=float, default=0,
                        help="Contaminated area in square metres")
    parser.add_argument("--env-persistence", type=int, default=None,
                        choices=[P_DAYS, P_MONTHS, P_YEARS, P_DECADES],
                        help=(f"Persistence factor P: {P_DAYS}=days-weeks, "
                              f"{P_MONTHS}=months-1yr, {P_YEARS}=1-10yrs, "
                              f"{P_DECADES}=decades/irreversible. "
                              "Overrides --hazard default."))
    parser.add_argument("--hazard", type=str, default=None,
                        choices=list(DEFAULT_PERSISTENCE.keys()),
                        help="Hazard type — automatically sets the default "
                             "persistence factor P when --env-persistence "
                             "is not specified")
    parser.add_argument("--population", type=int, default=0,
                        help="Number of people directly affected (service disruption headcount)")
    parser.add_argument("--loss", type=float, default=0,
                        help="Direct confirmed economic loss in USD "
                             "(exclude indirect/estimated losses)")
    parser.add_argument("--potential", type=float, default=None,
                        help="CPSS-Potential score (expert assessment; "
                             "included in vector string as /P:<value>)")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")
    parser.add_argument("--explain", action="store_true",
                        help="Show step-by-step calculation for each dimension")
    args = parser.parse_args()

    # Resolve persistence factor: explicit flag > hazard default > P_DAYS
    if args.env_persistence is not None:
        persistence = args.env_persistence
        p_source = f"--env-persistence {persistence}"
    elif args.hazard is not None:
        persistence = DEFAULT_PERSISTENCE[args.hazard]
        p_source = f"default for --hazard {args.hazard}"
    else:
        persistence = P_DAYS
        p_source = "default (no hazard specified)"

    result = assess(
        deaths=args.deaths,
        hospitalized=args.hospitalized,
        env_area_m2=args.env_area,
        env_persistence=persistence,
        population=args.population,
        loss_usd=args.loss,
    )

    vec = vector_string(result["H"], result["E"], result["I"], result["C"],
                        result["CPSS"], args.potential)

    if args.json:
        out = dict(result)
        out["vector"] = vec
        if args.potential is not None:
            out["CPSS_potential"] = args.potential
            out["class_potential"] = cpss_class(args.potential)
        print(json.dumps(out, indent=2))
        return

    print(f"H  (Human):          {result['H']:.2f}")
    print(f"E  (Environmental):  {result['E']:.2f}")
    print(f"I  (Infrastructure): {result['I']:.2f}")
    print(f"C  (Economic):       {result['C']:.2f}")
    print(f"CPSS-Actual:         {result['CPSS']:.2f}  [{result['class']}]")
    if args.potential is not None:
        print(f"CPSS-Potential:      {args.potential:.1f}  [{cpss_class(args.potential)}]")
    print(f"Vector:              {vec}")

    if args.explain:
        d, h_val = args.deaths, args.hospitalized
        print()
        print("--- Calculation details ---")
        print(f"H = log10({d}×100 + {h_val}×10 + 1)"
              f" = log10({d*100 + h_val*10 + 1})"
              f" = {result['H']:.4f}")
        if args.env_area > 0:
            product = args.env_area * persistence / 10
            print(f"E = log10({args.env_area:.0f} × {persistence} / 10)"
                  f" = log10({product:.2f})"
                  f" = {result['E']:.4f}  (P={persistence}: {p_source})")
        else:
            print("E = 0  (no contamination release)")
        if args.population > 0:
            print(f"I = log10({args.population} / 1000 + 1)"
                  f" = log10({args.population/1000 + 1:.4f})"
                  f" = {result['I']:.4f}")
        else:
            print("I = 0")
        if args.loss > 0:
            print(f"C = log10({args.loss:.0f} / 100000)"
                  f" = log10({args.loss/100000:.4f})"
                  f" = {result['C']:.4f}")
        else:
            print("C = 0  (no confirmed loss or below $100,000 threshold)")
        scores = [result['H'], result['E'], result['I'], result['C']]
        print(f"CPSS = max({result['H']:.2f}, {result['E']:.2f},"
              f" {result['I']:.2f}, {result['C']:.2f}) = {result['CPSS']:.2f}")


if __name__ == "__main__":
    main()
