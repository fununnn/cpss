# CPSS — Cyber-Physical Severity Scale

A logarithmic severity scale for cyberattacks against Industrial Control Systems (ICS)
that produce physical, environmental, and societal consequences.

## Why CPSS?

| Metric | Covers |
|--------|--------|
| CVSS | Software vulnerability exploitability |
| HAZOP / SIL | Industrial process safety risk |
| INES | Nuclear accidents only |
| **CPSS** | **Cyber attack → physical consequence → societal impact** |

No general scale existed for evaluating severity across the full chain from
cyber intrusion to physical outcome. CPSS fills that gap.

## Formula

```
CPSS = max(H, E, I, C)
```

| Dimension | Formula | Calibration |
|-----------|---------|-------------|
| H — Human | `log10(deaths × 100 + hospitalized × 10 + 1)` | H=4 ≈ 100 deaths |
| E — Environmental | `log10(area_m² × P / 10)` | E=4 ≈ 10,000 m² for months |
| I — Infrastructure | `log10(population / 1000 + 1)` | I=4 ≈ 10M people disrupted |
| C — Economic | `log10(loss_usd / 100000)` | C=4 ≈ $1B direct loss |

P = persistence factor: 1 (days), 10 (months), 100 (years), 1000 (decades/irreversible).

CPSS-Actual is fully deterministic — the same confirmed data always produces the
same score, with no analyst judgment required.

## Severity Classes

| CPSS | Class | Example |
|------|-------|---------|
| 0 | NONE | No measurable impact |
| >0–2 | LOW | Localised, contained |
| >2–4 | MODERATE | Facility-level disruption |
| >4–6 | SEVERE | Regional infrastructure disruption |
| >6–8 | CATASTROPHIC | National-scale impact |
| >8–10 | CRITICAL | Global or irreversible |

## Quick Start

```bash
# Chemical plant leak: 5,000 m² contaminated, 20,000 people affected, $80M loss
python3 src/cpss_calculator.py \
  --hazard chemical \
  --env-area 5000 \
  --population 20000 \
  --loss 80000000
```

```
H  (Human):          0.00
E  (Environmental):  4.70
I  (Infrastructure): 1.32
C  (Economic):       2.90
CPSS-Actual:         4.70  [SEVERE]
Vector:              CPSS:1.0/H:0.0/E:4.7/I:1.3/C:2.9/A:4.7
```

The `--hazard chemical` flag automatically sets P=100 (EPA CERCLA average cleanup duration).

Add `--potential <score>` to include CPSS-Potential in the vector string.
Add `--explain` to show step-by-step calculation.
Add `--json` for machine-readable output.

## Score an Incident in 5 Steps

1. **Hazard** — classify the physical hazard: `chemical / thermal / mechanical / electrical / radiological / hydrological / none`
2. **H** — count confirmed deaths and hospitalizations
3. **E** — estimate contaminated area (m²); use `--hazard` for default P, or `--env-persistence` to set P explicitly
4. **I** — count people who lost direct service access (not regional population)
5. **C** — sum direct confirmed losses in USD (exclude estimates and indirect losses)

Then: `CPSS = max(H, E, I, C)`

For CPSS-Potential, use the access-level rubric in `docs/cpss_spec.md §9`.

## Actual vs Potential

CPSS distinguishes two evaluations:

- **CPSS-Actual** — consequences that occurred
- **CPSS-Potential** — worst credible consequence given attacker access (Maximum Credible Accident)

A large gap (Potential − Actual) indicates that defenses, luck, or attacker restraint
prevented the worst outcome.

| Event | CPSS-Actual | CPSS-Potential | Gap |
|-------|-------------|----------------|-----|
| Maroochy Shire (2000) | 4 | 5 | 1 |
| Stuxnet (2010) | 3 | 6 | 3 |
| Ukraine Grid (2015) | 3 | 6 | 3 |
| Triton TRISIS (2017) | 2 | 7 | **5** |
| Colonial Pipeline (2021) | 3 | 5 | 2 |
| Volt Typhoon (2024) | 1 | 7 | **6** |

## Vector String

CPSS scores are expressed as a compact, machine-readable vector string:

```
CPSS:1.0/H:<h>/E:<e>/I:<i>/C:<c>/A:<actual>/P:<potential>
```

Example (Maroochy Shire, 2000):
```
CPSS:1.0/H:0.0/E:4.0/I:0.3/C:0.0/A:4.0/P:5.0
```

Include this string in incident reports to enable consistent, machine-readable
cross-incident comparison.

## Repository

```
cpss/
├── paper/
│   └── cpss_arxiv.tex       # arXiv preprint (Suzuki, 2026)
├── dataset/
│   └── cpss_incidents.csv   # 100 ICS incidents, 2000–2024
├── src/
│   └── cpss_calculator.py   # Reference implementation
└── docs/
    └── cpss_spec.md         # Full specification
```

## Dataset

`dataset/cpss_incidents.csv` contains 100 documented ICS cyber incidents (2000–2024),
covering power, water, oil & gas, manufacturing, and transportation sectors.

Each entry includes primary source reference, source type
(academic / government / vendor report / news), and confidence level.

CSV schema:
```
event, year, country, sector, scenario,
process_variable, process_deviation, hazard,
H, E, I, i_basis, C, cpss_actual, cpss_potential, class,
source, source_type, confidence
```

## Paper

Suzuki, S. (2026). *CPSS: A Severity Scale for Cyber-Physical Incidents in
Industrial Control Systems.* arXiv preprint.

Source: `paper/cpss_arxiv.tex`

## License

MIT
