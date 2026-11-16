EGLE MONITOR — Autonomous Spaceflight Clinical Decision Support System

**Team X-Band · NASA Space Apps Challenge 2026**

## Live Interactive Demo (Recommended Entry Point)

To test the system immediately without installing dependencies or running a local server, open the unified split-screen mission portal:

* **Live Interactive Portal:** [https://carlosmjg6301-bit.github.io/nasa/prototipo%20func/demo.htmL](https://carlosmjg6301-bit.github.io/nasa/prototipo%20func/demo.htmL)

This portal runs the **Autonomous Crew Clinical Console (`index.html`)** on the left and the **External Sensor Bus Emulator (`EGLE_TRANSMITTER.html`)** on the right in real time.

---

## 1. Executive Summary & Operational Problem

During deep-space exploration missions beyond Low Earth Orbit (such as Lunar Gateway, lunar surface operations, or Mars transit), two-way communication delays with Earth reach **20 to 48 minutes** and suffer multi-day blackouts during solar conjunction. Under these constraints, flight crews cannot rely on Mission Control in Houston to interpret raw biomedical or radiation-physics telemetry or wait for ground instructions during acute events.

**EGLE MONITOR** is an offline-first, edge-computing software and interface proposal built on deterministic clinical rules. It consolidates crew physiology, cabin Environmental Control and Life Support Systems (ECLSS), Extravehicular Mobility Unit (EMU) suit pressure, and—as its central pillar—ionizing space radiation dosimetry, translating NASA-validated hardware telemetry into plain-English guidance and step-by-step triage protocols for crew members without medical training.

---

## 2. Scientific Foundation & NASA Research Integration

All physiological envelopes, conversion equations, and response protocols are anchored in peer-reviewed aerospace medicine literature and NASA technical standards (`NASA-STD-3001 Vol. 1 & Vol. 2`, `OCHMO` Technical Briefs, `DOSMAP`, `MARE`, `Thermolab`, and `ARCHeR`):

* **Space Radiation & Personal Dosimetry (Core System Focus):**
  * Three-tier radiation monitoring: personal absorbed dose via Liulin-architecture silicon Mobile Dosimetry Units (**MDUs**, measuring absorbed dose rates in $\mu\text{Gy/h}$ and Linear Energy Transfer $\text{LET}$ spectra), internal cabin ambient radiation (complemented by secondary neutron spectrometers such as **CANS**), and external radiation flux to compute real-time hull shielding attenuation.
  * Autonomous edge processing: converts $\mu\text{Gy/h}$ to biological dose equivalent rates ($\text{mSv/h}$ and $\text{mSv/day}$) locally using the quality factor relationship $H = [D\ (\mu\text{Gy/h}) \times t\ (\text{h}) \div 1000] \times Q(\text{LET})$.
  * Thresholds and countermeasures: nominal range $0.02\text{–}0.04\text{ mSv/h}$; yellow caution band ($0.05\text{–}0.50\text{ mSv/h}$); red critical alert ($> 0.50\text{ mSv/h}$), switching MDU sampling from $90\text{ s}$ nominal intervals to $20\text{ s}$ **FAST Mode**, suspending tasks in lightly shielded modules, and directing all crew to the heavily shielded central core module above $1.0\text{ mSv/h}$ until rates drop below $0.10\text{ mSv/h}$. Tracks cumulative exposure against the $250\text{ mSv}$ 30-day/SPE limit and the $600\text{ mSv}$ career cap.
* **Biomedical Physiology & Wearable Telemetry:**
  * **Blood Glucose (CGM / Electrochemical Glucometer):** Tracks microgravity-induced insulin resistance using $G = (I - I_0)/S$ and $G = aV + b$. Nominal fasting range $70\text{–}99\text{ mg/dL}$ ($< 125\text{ mg/dL}$ post-meal), preventive warnings for mild hypoglycemia ($54\text{–}69\text{ mg/dL}$) or hyperglycemia ($126\text{–}180\text{ mg/dL}$), and emergency protocols for severe hypoglycemia ($< 54\text{ mg/dL}$) or DKA ketone risk ($\ge 250\text{ mg/dL}$).
  * **Blood Pressure (SBP, DBP & MAP):** Oscillometric estimation and Mean Arterial Pressure approximation $\text{MAP} = \text{DBP} + (\text{SBP} - \text{DBP})/3$, incorporating microgravity-specific hypotension protocols ($\text{SBP} < 90\text{ mmHg}$, avoiding Earth-standard leg elevation) and hypertensive crisis response ($> 180/120\text{ mmHg}$).
  * **Heart Rate (ECG / PPG):** Derived from beat-to-beat RR intervals ($\text{HR} = 60 / \text{RR}$) with personalized age-adjusted maximum heart rate ($HR_{\max} = 220 - \text{age}$) and an $85\%$ operational threshold for EVA operations.
  * **Body Temperature (Thermistors / RTD / Thermolab):** Computed via the Steinhart-Hart equation $1/T = A + B \cdot \ln(R) + C \cdot [\ln(R)]^3$, accounting for the $11\%$ reduction in evaporative heat loss in weightlessness and spaceflight-induced core temperature elevation ($\ge 37.5\text{ }^\circ\text{C}$ preventive, $\ge 38.0\text{ }^\circ\text{C}$ fever, $< 35.0\text{ }^\circ\text{C}$ hypothermia).
  * **Blood Oxygen ($\text{SpO}_2$) & Spacewalk (EVA / EMU):** Monitors sea-level normoxia ($101.3\text{ kPa}$, $P_IO_2 = 149\text{ mmHg}$, $\text{SpO}_2\ 97\text{–}100\%$), Artemis exploration atmosphere ($8.2\text{ psia} / 34\%\ \text{O}_2$, $\text{SpO}_2\ 94\text{–}96\%$), critical hypoxia ($< 90\%$), and EMU suit pressure regulation at $29.6\text{ kPa}$ ($4.3\text{ psia}$, $100\%\ \text{O}_2$).
  * **Renal Health & Bone Demineralization:** Discrete 24-hour body mass and urinary calcium logging with sex-specific hypercalciuria thresholds ($> 250\text{ mg/24h}$ female, $> 300\text{ mg/24h}$ male), urine volume ($< 2.0\text{ L/day}$), urine pH, Potassium Citrate ($\text{KCit } 20\text{ mEq/day}$), and ARED resistive exercise guidance (`OCHMO-MTB-003`).
* **Sleep & Behavioral Health (Blind Downlink Architecture):**
  * Tracks sleep duration via wrist actigraphy ($\ge 7.0\text{ h/night}$ target, $\ge 85\%$ efficiency, cumulative sleep debt) under orbital circadian disruption (16 sunrises per day).
  * Full item-by-item clinical questionnaires (**PHQ-9**, **GAD-7**, **PSQI**, and **POMS** subscales) executed with **zero local grading or mood feedback** shown to the astronaut; raw responses are sealed and queued exclusively for NASA behavioral health specialists on Earth.

---

## 3. System Architecture & Repository Layout

EGLE MONITOR decouples sensor acquisition, non-volatile persistence, and clinical triage using auditable deterministic rules (avoiding probabilistic Machine Learning models that could introduce medical hallucinations):

```text
nasa/
├── README.md                                  # Main project documentation
└── prototipo func/
    ├── demo.htmL                              # Unified split-screen judge testing portal
    ├── index.html                             # Autonomous Crew Clinical Console (React 18)
    ├── EGLE_TRANSMITTER.html                  # External biomedical & ECLSS sensor bus emulator
    ├── egle_mission_hub.py                    # Multithreaded Python 3 + SQLite + SHA-256 server
    ├── egle_mission.db                        # Non-volatile SQLite mission database
    └── docs/                                  # Referenced technical reports and annexes
