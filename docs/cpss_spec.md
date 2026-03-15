# CPSS Specification v1.0

Cyber-Physical Severity Scale — Technical Reference

---

## 1. Purpose

CPSS evaluates the severity of cyberattacks against Industrial Control
Systems (ICS) that produce physical, environmental, or societal consequences.

It estimates the **Worst Credible Consequence (WCC)** — the worst outcome
that is realistic given the attack scenario and system characteristics.
This concept corresponds to Maximum Credible Accident in safety engineering.

**Determinism guarantee.** CPSS-Actual is fully deterministic: given the four
numeric inputs (death toll, contaminated area and persistence factor, population
with service disruption, direct economic loss), the score is uniquely determined
by formula. No analyst judgment is required for CPSS-Actual. Subjectivity
enters only in CPSS-Potential, which the access-level rubric in §9 is designed
to constrain.

---

## 2. Incident Model

ICS cyber incidents follow this causal chain:

```
Cyber Attack
  └─ Attack Scenario
       └─ Control Manipulation
            └─ Process Deviation
                 └─ Hazard Release
                      └─ Exposure
                           └─ Propagation
                                └─ Impact → CPSS Score
```

---

## 3. Attack Scenarios

| Scenario | Description |
|----------|-------------|
| process_manipulation | Direct manipulation of process setpoints or commands |
| safety_system_disable | Disabling or bypassing safety instrumented systems |
| sensor_spoofing | Injecting false sensor readings |
| control_logic_modification | Modifying PLC/DCS logic |
| remote_shutdown | Unauthorized shutdown of operations |
| supply_chain_compromise | Malicious code introduced via vendor or update |

---

## 4. Process Deviation Model (HAZOP-based)

Process Deviation = Variable + Deviation

**Variables:** temperature, pressure, flow, level, speed, voltage

**Deviations:** more, less, none, reverse, unstable

| Example | Consequence |
|---------|-------------|
| temperature + more | Overheating → thermal runaway |
| pressure + more | Overpressure → rupture |
| flow + none | Cooling loss → meltdown |
| speed + reverse | Mechanical damage |

---

## 5. Hazard Taxonomy

| Hazard | Description |
|--------|-------------|
| chemical | Toxic or flammable substance release |
| thermal | Fire, explosion, heat |
| mechanical | Equipment failure, structural damage |
| electrical | Arc flash, grid instability |
| radiological | Radioactive material release |
| hydrological | Uncontrolled water or sewage release |
| none | No physical hazard triggered (reconnaissance, IT-only) |

---

## 6. Impact Dimensions

CPSS evaluates four dimensions, each scored 0–10.

### 6.1 Human Impact (H)

```
H = log10(deaths × 100 + hospitalized × 10 + 1)
```

| H | Deaths | Hospitalized (deaths = 0) |
|---|--------|---------------------------|
| 0 | 0 | 0 |
| 2 | ~1 | ~10 |
| 3 | ~10 | ~100 |
| 4 | ~100 | ~1,000 |
| 5 | ~1,000 | ~10,000 |
| 6 | ~10,000 | ~100,000 |
| 7 | ~100,000 | ~1,000,000 |

Counts direct fatalities and confirmed hospitalizations attributable to the incident.
The hospitalized weight (×10) reflects approximately 1/10 of a fatality,
consistent with disability-adjusted life year (DALY) disability weights for
serious injury requiring hospitalization.
H = 0 when deaths = 0 and hospitalized = 0; H > 0 for any confirmed fatality or hospitalization.

**Calibration rationale:** The ×100 multiplier is anchored to the value of statistical life (VSL ≈ $10M, per U.S. EPA guidance). At this VSL, 100 fatalities imply a societal cost of ~$1B, corresponding to C = 4. This creates cross-dimensional consistency: H = 4 (100 deaths) ≈ I = 4 (10M people disrupted) ≈ C = 4 ($1B loss). In practice, H takes values in {0} ∪ [2, 10]; the interval (0, 2) is unreachable for integer death counts.

### 6.2 Environmental Impact (E)

```
E = log10(area_m² × P / 10)    # E = 0 when no contamination release
```

`area_m²` = contaminated area in square metres
`P` = persistence factor (see table below); cap E at 10

**Persistence factor P:**

| P | Duration | Reference baseline |
|---|----------|--------------------|
| 1 | Days to weeks; complete natural recovery | WHO drinking-water guidelines |
| 10 | Months to one year | EPA SPCC oil spill response guidance |
| 100 | One to ten years | EPA CERCLA average cleanup duration (~7 years) |
| 1000 | Decades or irreversible | IAEA post-accident decontamination standards |

When incident-specific remediation data are not available, use the default P by
hazard category below. Observed values take precedence over defaults.

**Default P by hazard category:**

| Hazard | Default P | Notes |
|--------|-----------|-------|
| mechanical | 1 | Physical damage only; no chemical release |
| electrical | 1–10 | 10 if PCB or transformer oil released |
| hydrological | 10 | Biological recovery months to one year |
| thermal | 10–100 | 100 for hydrocarbon soil contamination |
| chemical | 100 | CERCLA average remediation duration |
| radiological | 1000 | Half-life dependent; typically decades or longer |

**Calibration reference values:**

| E | area_m² | P | Typical scenario |
|---|---------|---|-----------------|
| 2 | ~100 | 10 | Building contamination, months |
| 4 | ~10,000 | 10 | Local pollution, months |
| 6 | ~1,000,000 | 10 | 1 km² contamination, months |
| 8 | ~10,000,000 | 100 | 10 km² contamination, years |

**Estimating area_m²:**

Use the method appropriate to the hazard type. Observed remediation or
regulatory survey data take precedence over estimates.

| Hazard | Estimation method |
|--------|------------------|
| Chemical | Area where soil/groundwater concentrations exceed regulatory cleanup standards (EPA RSL; ECHA PNEC) |
| Radiological | Area where dose rate exceeds IAEA intervention level (reference: 1 mSv/yr; IAEA GSG-11) |
| Hydrological | Surface area of affected water body (river reach, lake, or coastal zone from field survey or hydrological model) |
| Thermal | Combined footprint of direct burn area and hydrocarbon soil contamination (from fire investigation report) |
| Mechanical | Debris field boundary or structural collapse footprint (from incident investigation report) |
| Electrical | Area of direct transformer oil or PCB spill (from field inspection report) |

When no incident-specific area data are available, use a conservative lower-bound
estimate based on facility footprint and plausible release volume.

### 6.3 Infrastructure Impact (I)

```
I = log10(population directly affected / 1000 + 1)
```

| I | Population |
|---|------------|
| 1 | ~10,000 |
| 2 | ~100,000 |
| 3 | ~1,000,000 |
| 4 | ~10,000,000 |
| 5 | ~100,000,000 |
| 6 | ~1,000,000,000 |

**Definition:** Population who experienced direct service interruption.
Does not include the general regional population of the affected area.

**Calibration note:** At the same score level, 100 deaths (H) corresponds to
approximately 10 million people with service disruption (I), reflecting
the greater per-person severity of fatality versus temporary disruption.

**Exception for hazard=none entries (`i_basis = ics_systems`):**
For ICS-scoped reconnaissance incidents where no physical process was manipulated,
no population experienced a service disruption. I is instead computed as:

```
I_access = log10(compromised ICS systems + 1)
```

The `i_basis` field in the CSV records which interpretation applies:
`population` (standard formula) or `ics_systems` (hazard=none exception).
Do not compare I values across these two bases directly.

Fallback rules when ICS system count is not available:
- ICS control systems confirmed accessed/compromised, count unknown → I = 2
- No ICS control system access confirmed (reconnaissance or adjacent network only) → I = 0

### 6.4 Economic Impact (C)

```
C = log10(loss_usd / 100000)    # loss = 0 → C = 0
```

| C | Loss |
|---|------|
| 2 | ~$10M |
| 3 | ~$100M |
| 4 | ~$1B |
| 5 | ~$10B |
| 6 | ~$100B |
| 7 | ~$1T |

**Definition:** Direct, confirmed economic losses only.
Indirect, estimated, or downstream losses are excluded.
Losses below $100,000 USD yield a negative log value and are treated as C = 0.

---

## 7. CPSS Score

```
CPSS = max(H, E, I, C)
```

Overall severity is determined by the dominant impact dimension,
following the design principle used in established disaster scales
(seismic magnitude, INES).

### Empirical note

In ICS cyber incidents, H rarely dominates the CPSS score.
Of the 100 incidents in the dataset, H > 0 in only two cases
(Chatsworth Train Collision, 2008: H = 3.6;
Taum Sauk Dam SCADA Overflow, 2005: H = 1.6);
in both, another dimension exceeds H (C = 3.7 and E = 6.6, respectively),
so H is the dominant dimension in zero incidents.
ICS attacks typically seek infrastructure disruption rather than
direct casualties, and safety systems often limit human harm
even when process integrity is compromised.
I and C are the dominant dimensions in most documented incidents.

---

## 7b. Vector String Notation

To preserve multi-dimensional information beyond the scalar score,
CPSS defines a compact vector string:

```
CPSS:1.0/H:<h>/E:<e>/I:<i>/C:<c>/A:<actual>/P:<potential>
```

All values rounded to one decimal place. `CPSS:1.0` identifies the spec version.
The `/P:` field is included only when CPSS-Potential has been assessed.

**Example** (Maroochy Shire, 2000):
```
CPSS:1.0/H:0.0/E:4.0/I:0.3/C:0.0/A:4.0/P:5.0
```

Include the vector string in incident reports to enable consistent,
machine-readable cross-incident comparison. The reference implementation
(`src/cpss_calculator.py`) outputs the vector string automatically.

---

## 8. Severity Classes

| CPSS | Class | Example |
|------|-------|---------|
| 0 | NONE | No measurable impact |
| >0–2 | LOW | Localised, contained |
| >2–4 | MODERATE | Facility-level disruption |
| >4–6 | SEVERE | Regional infrastructure disruption |
| >6–8 | CATASTROPHIC | National-scale impact |
| >8–10 | CRITICAL   | Global or irreversible |

---

## 9. Actual vs Potential Severity

| Evaluation | Definition |
|------------|------------|
| CPSS-Actual | Score based on consequences that occurred |
| CPSS-Potential | Score based on worst credible consequence given attack access |

A large gap (Potential − Actual) indicates that defenses, luck, or
attacker restraint prevented the worst outcome.

**CPSS-Potential assessment rubric (attacker access → max credible score):**

| Attacker Access Level | Max Credible CPSS-Potential | Basis |
|-----------------------|-----------------------------|-------|
| IT network only (OT isolated) | ≤ 4 | No direct process control |
| OT-adjacent (HMI, historian, DMZ) | ≤ 5 | Limited process influence |
| OT control system reached (PLC/DCS) | ≤ 6 | Process deviation achievable |
| Safety system reached (SIS/SIL) | ≤ 7 | Last-line defense intact |
| Safety system disabled or bypassed | ≤ 8 | No automated safeguard |
| Multiple facilities or national grid | ≤ 9 | Cascading failure possible |

Incident-specific evidence takes precedence over rubric defaults.
Analysts may assign lower values when the hazard profile does not support
a higher consequence at the given access level.

**Example — Triton TRISIS (2017):**
- CPSS-Actual = 2 (no accident occurred)
- CPSS-Potential = 7 (safety system disabled; petrochemical explosion possible)
- Gap = 5

---

## 10. Dataset Inclusion Criteria

The dataset (`dataset/cpss_incidents.csv`) targets **ICS/OT cyber incidents**
and applies the following inclusion rules.

### Inclusion

| Category | Inclusion condition | Scoring approach |
|----------|--------------------|--------------------|
| OT direct impact | Control manipulation or physical process disruption confirmed | Full H/E/I/C evaluation |
| IT→OT cascade | IT attack that caused physical shutdown or OT consequence | Full H/E/I/C; note cascade in scenario |
| ICS-scoped reconnaissance | Attack explicitly targeted ICS/OT systems or vendors; OT compromise reached | hazard=none; CPSS-Actual from cleanup costs only; CPSS-Potential reflects access achieved |
| ICS near-miss | Attacker reached OT-adjacent layer (e.g. engineering workstation, safety PLC) but no process deviation occurred | hazard=none; CPSS-Actual low; CPSS-Potential reflects worst credible consequence |

### Exclusion

The following are **excluded** from the dataset:

- Pure IT attacks (ransomware, wipers) where OT systems were isolated and unaffected
- IT espionage not scoped to ICS/OT systems or vendors
- Healthcare, enterprise, or general IT incidents without ICS component
- Incidents where public evidence is limited to a single unverified report (confidence = low)

### Scoring ICS-scoped reconnaissance entries

For entries with `hazard=none` (no physical process manipulated):

- **H, E** = 0
- **I** = log₁₀(number of compromised ICS systems + 1), using system count
  rather than population (formula exception for hazard=none).
  - If ICS control systems were confirmed accessed/compromised but count is unknown: use I = 2 as a conservative fallback.
  - If no ICS control system access was confirmed (targeting, reconnaissance, or adjacent-network access only): use I = 0.
- **C** = log₁₀(investigation and remediation cost / 100000), typically 1 ($1M range)
- **CPSS-Actual** = max(H, E, I, C) — reflects access impact, not physical consequence
- **CPSS-Potential** — assess what physical consequence was achievable given
  the attacker's access and the target system's hazard profile

---

## 11. Dataset Schema

File: `dataset/cpss_incidents.csv`

| Field | Type | Description |
|-------|------|-------------|
| event | string | Incident name |
| year | int | Year of incident |
| country | string | Country of occurrence |
| sector | string | Industry sector |
| scenario | string | Attack scenario (see §3) |
| process_variable | string | Affected process variable |
| process_deviation | string | Type of deviation (HAZOP) |
| hazard | string | Physical hazard type (see §5) |
| H | float | Human impact score |
| E | float | Environmental impact score |
| I | float | Infrastructure impact score |
| i_basis | string | Basis for I: `population` (service disruption headcount) or `ics_systems` (hazard = none entries, where I counts compromised control systems) |
| C | float | Economic impact score |
| cpss_actual | float | CPSS-Actual = max(H,E,I,C) |
| cpss_potential | float | CPSS-Potential (expert assessment) |
| class | string | Severity class label |
| source | string | Primary reference for the incident |
| source_type | string | academic / government / vendor_report / news |
| confidence | string | high / medium / low — completeness of public information |

---

## 12. Scoring Checklist

Use this checklist to score any ICS cyber incident consistently.

**Step 1 — Classify hazard**
Identify the physical hazard released: `chemical / thermal / mechanical / electrical / radiological / hydrological / none`

**Step 2 — Score H**
Count confirmed fatalities and hospitalizations.
Compute: `H = log10(deaths × 100 + hospitalized × 10 + 1)`

**Step 3 — Score E**
- If no contamination release: `E = 0`
- Otherwise: estimate contaminated area in m² using §6.2 estimation guide
- Assign P from the hazard default table (or use observed remediation data)
- Compute: `E = log10(area_m² × P / 10)`; cap at 10

**Step 4 — Score I**
- Count people who lost direct service access (not regional population)
- For `hazard=none` entries: count compromised ICS systems instead
- Compute: `I = log10(population / 1000 + 1)` or `log10(ics_systems + 1)`

**Step 5 — Score C**
- Sum direct confirmed losses in USD (exclude estimates and indirect losses)
- Compute: `C = log10(loss_usd / 100000)`; treat negative values as 0

**Result**
`CPSS-Actual = max(H, E, I, C)`

For **CPSS-Potential**: identify the highest attacker access level confirmed,
consult the rubric in §9, and assess the worst credible physical consequence
achievable from that access level given the target system's hazard profile.

**Output vector string** using the reference implementation:
```bash
python3 src/cpss_calculator.py --hazard <type> --env-area <m²> \
    --population <n> --loss <usd> --potential <score>
```
