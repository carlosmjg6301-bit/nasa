import tkinter as tk
from tkinter import font as tkfont


TELEMETRY_DATA = {
    "HB": {
        "Radiation": {
            "short_label": "Radiation",
            "title": "RADIATION DOSE",
            "value": "0.42",
            "unit": "mSv/d",
            "status": "NOMINAL",
            "status_color": "#22c55e",
            "protocol": [
                "1. Verify personal dosimeter sync with spacecraft telemetry.",
                "2. Compare internal tissue-equivalent phantom vs. skin dose.",
                "3. Log cumulative mission exposure against 30-day career limits.",
                "4. Confirm storm-shelter bulkhead readiness if flux rises.",
            ],
            "recommendations": [
                "Maintain standard crew station rotation; avoid prolonged proximity to unshielded hull segments.",
                "Administer scheduled antioxidant protocol and log baseline lymphocyte count at next medical check.",
            ],
        },
        "HR": {
            "short_label": "HR",
            "title": "HEART RATE",
            "value": "60",
            "unit": "bpm",
            "status": "NOMINAL",
            "status_color": "#22c55e",
            "protocol": [
                "1. Acquire 3-lead ECG waveform and verify R-R interval stability.",
                "2. Cross-check resting heart rate against pre-flight supine baseline.",
                "3. Evaluate orthostatic tolerance index prior to resistive exercise.",
                "4. Record autonomic recovery slope 2 minutes post-activity.",
            ],
            "recommendations": [
                "Cardiovascular rhythm and resting rate are optimal for microgravity baseline.",
                "Proceed with scheduled 45-minute ARED resistive and cycle ergometer countermeasure session.",
            ],
        },
        "Blood Sugar": {
            "short_label": "Blood Sugar",
            "title": "BLOOD SUGAR",
            "value": "100",
            "unit": "mg/dL",
            "status": "NOMINAL",
            "status_color": "#22c55e",
            "protocol": [
                "1. Validate continuous interstitial glucose sensor calibration.",
                "2. Correlate current reading with last caloric intake timestamp.",
                "3. Monitor insulin sensitivity shifts induced by cephalad fluid shift.",
                "4. Flag glycemic excursions below 70 mg/dL or above 140 mg/dL.",
            ],
            "recommendations": [
                "Euglycemic state confirmed; maintain balanced complex-carbohydrate ration prior to EVA prep.",
                "Ensure 500 mL electrolyte hydration intake over the next 2 hours.",
            ],
        },
        "SpO2": {
            "short_label": "SpO2",
            "title": "BLOOD OXYGEN (SpO2)",
            "value": "92",
            "unit": "%",
            "status": "ADVISORY",
            "status_color": "#f59e0b",
            "protocol": [
                "1. Confirm pulse oximeter perfusion index on warm peripheral digit.",
                "2. Cross-reference cabin ppO2 and ppCO2 partial pressure sensors.",
                "3. Assess crew member for mild headache, dyspnea, or fatigue.",
                "4. Repeat measurement after 3 minutes of paced diaphragmatic breathing.",
            ],
            "recommendations": [
                "Borderline peripheral saturation (92%) detected—verify cabin O2 partial pressure (target 21.3 kPa).",
                "Initiate controlled breathing protocol and re-evaluate SpO2 within 10 minutes; prepare supplemental O2 if < 90%.",
            ],
        },
        "Body Temperature": {
            "short_label": "Body Temperature",
            "title": "BODY TEMPERATURE",
            "value": "37.0",
            "unit": "°C",
            "status": "NOMINAL",
            "status_color": "#22c55e",
            "protocol": [
                "1. Read core tympanic/skin-flux thermometry telemetry stream.",
                "2. Account for altered convective heat dissipation in zero-G.",
                "3. Check liquid cooling garment (LCG) loop inlet/outlet delta.",
                "4. Monitor circadian core temperature nadir during sleep cycle.",
            ],
            "recommendations": [
                "Core thermoregulation is stable at 37.0 °C with normal peripheral heat dissipation.",
                "Keep cabin airflow fans at nominal speed to prevent localized thermal boundary layers.",
            ],
        },
    },
    "AMBIENT": {
        "Radiation": {
            "short_label": "Radiation",
            "title": "CABIN RADIATION",
            "value": "0.38",
            "unit": "mSv/d",
            "status": "NOMINAL",
            "status_color": "#22c55e",
            "protocol": [
                "1. Poll internal dosimetry nodes across crew quarters and lab.",
                "2. Compare GCR background vs. trapped belt pass spikes.",
                "3. Verify polyethylene water-wall shielding integrity.",
                "4. Sync internal Matrushka-equivalent phantom channel logs.",
            ],
            "recommendations": [
                "Internal cabin shielding attenuation is operating within expected parameters.",
                "No crew relocation required during current orbital inclination pass.",
            ],
        },
        "HR": {
            "short_label": "HR",
            "title": "CREW AVG HR",
            "value": "64",
            "unit": "bpm",
            "status": "NOMINAL",
            "status_color": "#22c55e",
            "protocol": [
                "1. Aggregate anonymized biometric bus across active cabin crew.",
                "2. Correlate collective heart rate trends with cabin CO2 levels.",
                "3. Monitor workload stress spikes during docking or payload ops.",
                "4. Verify wireless telemetry packet integrity from wearables.",
            ],
            "recommendations": [
                "Cabin crew physiological workload remains within nominal resting-to-light-activity range.",
                "Maintain current work-rest scheduling cadence.",
            ],
        },
        "Blood Sugar": {
            "short_label": "Blood Sugar",
            "title": "NUTRITION INDEX",
            "value": "98",
            "unit": "mg/dL",
            "status": "NOMINAL",
            "status_color": "#22c55e",
            "protocol": [
                "1. Track post-prandial metabolic telemetry across crew shift.",
                "2. Verify galley water dispenser temperature for rehydration packs.",
                "3. Log caloric intake compliance against mission nutrition plan.",
                "4. Check cold-storage telemetry for biomedical samples.",
            ],
            "recommendations": [
                "Crew metabolic stability is nominal following scheduled meal period.",
                "Continue standard microgravity nutrient and micronutrient supplementation.",
            ],
        },
        "SpO2": {
            "short_label": "SpO2",
            "title": "CABIN O2 LEVEL",
            "value": "20.9",
            "unit": "% O2",
            "status": "NOMINAL",
            "status_color": "#22c55e",
            "protocol": [
                "1. Read primary and redundant mass spectrometer O2 channels.",
                "2. Verify CO2 scrubber (CDRA) bed regeneration cycle.",
                "3. Confirm total cabin pressure holds at 101.3 kPa.",
                "4. Check trace contaminant control assembly airflow.",
            ],
            "recommendations": [
                "Cabin atmospheric composition is balanced; ppCO2 remains below 3.0 mmHg.",
                "No O2 generator boost required.",
            ],
        },
        "Body Temperature": {
            "short_label": "Body Temperature",
            "title": "CABIN AIR TEMP",
            "value": "22.5",
            "unit": "°C",
            "status": "NOMINAL",
            "status_color": "#22c55e",
            "protocol": [
                "1. Monitor inter-module thermal control loop heat exchangers.",
                "2. Verify relative humidity stays within 40%–55% RH.",
                "3. Check avionics rack exhaust cooling airflow.",
                "4. Balance cabin setpoint ahead of crew sleep period.",
            ],
            "recommendations": [
                "Cabin thermal environment is comfortable and prevents condensation on hull surfaces.",
                "Maintain current heat-exchanger valve modulation.",
            ],
        },
    },
    "EXTERNAL": {
        "Radiation": {
            "short_label": "Radiation",
            "title": "EXTERNAL FLUX",
            "value": "1.85",
            "unit": "mSv/d",
            "status": "ELEVATED",
            "status_color": "#ef4444",
            "protocol": [
                "1. Monitor external hull dosimeter and solar particle spectrometer.",
                "2. Compute dose differential between external sensor and cabin interior.",
                "3. Track South Atlantic Anomaly (SAA) orbital entry window.",
                "4. Evaluate EVA radiation go/no-go threshold criteria.",
            ],
            "recommendations": [
                "External unshielded flux elevated during high-latitude pass—defer non-essential EVA tasks.",
                "Keep hatch thermal/micrometeoroid cover closed until flux drops below 0.80 mSv/d.",
            ],
        },
        "HR": {
            "short_label": "HR",
            "title": "EVA SUIT HR",
            "value": "112",
            "unit": "bpm",
            "status": "ACTIVE",
            "status_color": "#38bdf8",
            "protocol": [
                "1. Monitor suit biometric harness during external translation.",
                "2. Estimate metabolic heat production (BTU/hr) from heart rate.",
                "3. Cross-check suit O2 consumption rate against reserve tank.",
                "4. Alert Flight Surgeon if sustained HR exceeds 150 bpm.",
            ],
            "recommendations": [
                "Metabolic expenditure aligns with moderate upper-body EVA translation.",
                "Schedule a 5-minute tether pause before high-torque tool operations.",
            ],
        },
        "Blood Sugar": {
            "short_label": "Blood Sugar",
            "title": "EVA METABOLIC",
            "value": "108",
            "unit": "mg/dL",
            "status": "NOMINAL",
            "status_color": "#22c55e",
            "protocol": [
                "1. Track continuous glucose trend during extended suit operations.",
                "2. Verify in-suit drink bag (IDB) fluid level.",
                "3. Monitor for hypoglycemia signs during high metabolic exertion.",
                "4. Log pre-airlock repressurization metabolic status.",
            ],
            "recommendations": [
                "Glycemic reserves are steady for remaining EVA timeline.",
                "Prompt crew member to sip from in-suit drink bag at next workstation.",
            ],
        },
        "SpO2": {
            "short_label": "SpO2",
            "title": "SUIT ppO2 / SpO2",
            "value": "99",
            "unit": "%",
            "status": "NOMINAL",
            "status_color": "#22c55e",
            "protocol": [
                "1. Verify 100% O2 suit loop pressure at 29.6 kPa (4.3 psi).",
                "2. Monitor LiOH / Metox CO2 removal canister saturation.",
                "3. Confirm helmet visor anti-fog and purge valve status.",
                "4. Track peripheral oximetry ear-clip sensor signal.",
            ],
            "recommendations": [
                "Pure oxygen suit loop maintains 99% arterial saturation with zero decompression symptoms.",
                "Continue nominal EVA oxygen regulator operation.",
            ],
        },
        "Body Temperature": {
            "short_label": "Body Temperature",
            "title": "EXT HULL / LCG",
            "value": "36.8",
            "unit": "°C",
            "status": "NOMINAL",
            "status_color": "#22c55e",
            "protocol": [
                "1. Compare external thermal extremes (-120 °C to +120 °C) vs. suit.",
                "2. Regulate Liquid Cooling Garment (LCG) sublimator flow.",
                "3. Monitor glove heater circuits during orbital night pass.",
                "4. Verify core temperature stays between 36.5 °C and 37.8 °C.",
            ],
            "recommendations": [
                "LCG thermal loop effectively rejecting metabolic heat during sunlit orbital phase.",
                "Increase glove thermal setting by +1 step prior to eclipse entry.",
            ],
        },
    },
}

PARAM_ORDER = ["Radiation", "HR", "Blood Sugar", "SpO2", "Body Temperature"]


class EgleTelemetrySlideApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EGLE MONITOR — Telemetry Slide Platform")
        self.configure(bg="#090d16")

        self.current_layer = "HB"
        self.current_param = "HR"
        self.is_fullscreen = True

        # Start in fullscreen slide mode
        self.geometry("1280x800")
        self.attributes("-fullscreen", True)

        # Keyboard shortcuts for slide navigation & fullscreen control
        self.bind("<Escape>", self.exit_fullscreen)
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Up>", lambda e: self.step_slide(-1))
        self.bind("<Down>", lambda e: self.step_slide(1))

        self._setup_fonts()
        self._build_layout()
        self.refresh_ui()

    def _setup_fonts(self):
        self.font_nav_title = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.font_nav_value = tkfont.Font(family="Helvetica", size=20, weight="bold")
        self.font_pill = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.font_section = tkfont.Font(family="Helvetica", size=18, weight="bold")
        self.font_body = tkfont.Font(family="Helvetica", size=13)
        self.font_hero_title = tkfont.Font(family="Helvetica", size=28, weight="bold")
        self.font_hero_value = tkfont.Font(family="Helvetica", size=72, weight="bold")
        self.font_hero_unit = tkfont.Font(family="Helvetica", size=26, weight="bold")
        self.font_badge = tkfont.Font(family="Helvetica", size=11, weight="bold")

    def _build_layout(self):
        # Main 2-column grid: Left sidebar column (buttons), Right main display area
        self.grid_columnconfigure(0, weight=0, minsize=260)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= LEFT COLUMN: VERTICAL PARAMETER CUBES =================
        self.left_col = tk.Frame(self, bg="#0d1320", highlightbackground="#263248", highlightthickness=2)
        self.left_col.grid(row=0, column=0, sticky="nsew", padx=(14, 7), pady=14)
        self.left_col.grid_columnconfigure(0, weight=1)

        self.nav_cards = {}
        for idx, param_key in enumerate(PARAM_ORDER):
            self.left_col.grid_rowconfigure(idx, weight=1)
            card = tk.Frame(
                self.left_col,
                bg="#131c2e",
                highlightbackground="#2b3a55",
                highlightthickness=2,
                cursor="hand2",
            )
            card.grid(row=idx, column=0, sticky="nsew", padx=8, pady=6)
            card.grid_propagate(False)

            lbl_name = tk.Label(
                card,
                text=param_key,
                font=self.font_nav_title,
                fg="#94a3b8",
                bg="#131c2e",
                anchor="w",
            )
            lbl_name.pack(fill="x", padx=16, pady=(14, 2))

            lbl_val = tk.Label(
                card,
                text="--",
                font=self.font_nav_value,
                fg="#f8fafc",
                bg="#131c2e",
                anchor="w",
            )
            lbl_val.pack(fill="x", padx=16, pady=(0, 12))

            # Bind click across frame and child labels (macOS-safe button behavior)
            for widget in (card, lbl_name, lbl_val):
                widget.bind("<Button-1>", lambda e, k=param_key: self.select_param(k))

            self.nav_cards[param_key] = {
                "frame": card,
                "name": lbl_name,
                "value": lbl_val,
            }

        # ================= RIGHT AREA: MAIN TELEMETRY SLIDE =================
        self.right_area = tk.Frame(self, bg="#0d1320", highlightbackground="#263248", highlightthickness=2)
        self.right_area.grid(row=0, column=1, sticky="nsew", padx=(7, 14), pady=14)
        self.right_area.grid_columnconfigure(0, weight=1)
        self.right_area.grid_rowconfigure(0, weight=0)  # Top Header Pill
        self.right_area.grid_rowconfigure(1, weight=3)  # Middle Split (Protocol | Readout)
        self.right_area.grid_rowconfigure(2, weight=2)  # Bottom (Recommendations)

        # --- Top Header Bar: HB | AMBIENT | EXTERNAL + Fullscreen Control ---
        top_bar = tk.Frame(self.right_area, bg="#0d1320")
        top_bar.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 10))

        pill_container = tk.Frame(
            top_bar,
            bg="#131c2e",
            highlightbackground="#38bdf8",
            highlightthickness=2,
        )
        pill_container.pack(side="left")

        self.layer_buttons = {}
        for layer in ["HB", "AMBIENT", "EXTERNAL"]:
            lbl = tk.Label(
                pill_container,
                text=layer,
                font=self.font_pill,
                padx=18,
                pady=6,
                cursor="hand2",
            )
            lbl.pack(side="left", padx=3, pady=3)
            lbl.bind("<Button-1>", lambda e, l=layer: self.select_layer(l))
            self.layer_buttons[layer] = lbl

        # Slide status & Fullscreen button on top-right
        controls_frame = tk.Frame(top_bar, bg="#0d1320")
        controls_frame.pack(side="right")

        self.lbl_slide_counter = tk.Label(
            controls_frame,
            text="SLIDE 2 / 5  (↑ ↓)",
            font=self.font_badge,
            fg="#64748b",
            bg="#0d1320",
        )
        self.lbl_slide_counter.pack(side="left", padx=(0, 14))

        self.btn_fullscreen = tk.Label(
            controls_frame,
            text="⛶ FULLSCREEN (F11)",
            font=self.font_badge,
            fg="#38bdf8",
            bg="#131c2e",
            highlightbackground="#2b3a55",
            highlightthickness=1,
            padx=12,
            pady=6,
            cursor="hand2",
        )
        self.btn_fullscreen.pack(side="left")
        self.btn_fullscreen.bind("<Button-1>", self.toggle_fullscreen)

        # --- Middle Split Frame: Protocol (Left) | Giant Readout (Right) ---
        mid_frame = tk.Frame(self.right_area, bg="#0d1320")
        mid_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=6)
        mid_frame.grid_columnconfigure(0, weight=5)
        mid_frame.grid_columnconfigure(1, weight=6)
        mid_frame.grid_rowconfigure(0, weight=1)

        # Protocol Box
        protocol_box = tk.Frame(
            mid_frame,
            bg="#111927",
            highlightbackground="#2b3a55",
            highlightthickness=2,
        )
        protocol_box.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(
            protocol_box,
            text="Protocol",
            font=self.font_section,
            fg="#f8fafc",
            bg="#111927",
            anchor="w",
        ).pack(fill="x", padx=20, pady=(16, 10))

        self.lbl_protocol_steps = tk.Label(
            protocol_box,
            text="",
            font=self.font_body,
            fg="#cbd5e1",
            bg="#111927",
            justify="left",
            anchor="nw",
            wraplength=390,
        )
        self.lbl_protocol_steps.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        # Schematic Astronaut / Subject Icon Canvas (matches boxed figure in sketch)
        icon_row = tk.Frame(protocol_box, bg="#111927")
        icon_row.pack(fill="x", padx=20, pady=(0, 16))

        self.icon_canvas = tk.Canvas(
            icon_row,
            width=74,
            height=74,
            bg="#0b111e",
            highlightbackground="#38bdf8",
            highlightthickness=2,
        )
        self.icon_canvas.pack(side="left")
        self._draw_subject_icon()

        self.lbl_protocol_note = tk.Label(
            icon_row,
            text="ACTIVE TELEMETRY PROTOCOL\nBiomedical Telemetry Link: LOCKED",
            font=self.font_badge,
            fg="#38bdf8",
            bg="#111927",
            justify="left",
        )
        self.lbl_protocol_note.pack(side="left", padx=14)

        # Hero Readout Box (Right Side of Middle Split)
        hero_box = tk.Frame(
            mid_frame,
            bg="#111927",
            highlightbackground="#2b3a55",
            highlightthickness=2,
        )
        hero_box.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        hero_inner = tk.Frame(hero_box, bg="#111927")
        hero_inner.place(relx=0.5, rely=0.5, anchor="center")

        self.lbl_status_badge = tk.Label(
            hero_inner,
            text="● NOMINAL",
            font=self.font_badge,
            fg="#22c55e",
            bg="#0b111e",
            padx=12,
            pady=4,
        )
        self.lbl_status_badge.pack(pady=(0, 12))

        self.lbl_hero_title = tk.Label(
            hero_inner,
            text="HEART RATE",
            font=self.font_hero_title,
            fg="#f8fafc",
            bg="#111927",
        )
        self.lbl_hero_title.pack(pady=(0, 10))

        val_row = tk.Frame(hero_inner, bg="#111927")
        val_row.pack()

        self.lbl_hero_value = tk.Label(
            val_row,
            text="60",
            font=self.font_hero_value,
            fg="#38bdf8",
            bg="#111927",
        )
        self.lbl_hero_value.pack(side="left")

        self.lbl_hero_unit = tk.Label(
            val_row,
            text=" bpm",
            font=self.font_hero_unit,
            fg="#94a3b8",
            bg="#111927",
        )
        self.lbl_hero_unit.pack(side="left", anchor="s", pady=(0, 14))

        # --- Bottom Box: Recommendations ---
        rec_box = tk.Frame(
            self.right_area,
            bg="#111927",
            highlightbackground="#2b3a55",
            highlightthickness=2,
        )
        rec_box.grid(row=2, column=0, sticky="nsew", padx=18, pady=(8, 16))

        tk.Label(
            rec_box,
            text="Recommendations",
            font=self.font_section,
            fg="#f8fafc",
            bg="#111927",
            anchor="w",
        ).pack(fill="x", padx=20, pady=(14, 8))

        self.lbl_recommendations = tk.Label(
            rec_box,
            text="",
            font=self.font_body,
            fg="#e2e8f0",
            bg="#111927",
            justify="left",
            anchor="nw",
            wraplength=860,
        )
        self.lbl_recommendations.pack(fill="both", expand=True, padx=20, pady=(0, 14))

    def _draw_subject_icon(self):
        c = self.icon_canvas
        c.delete("all")
        # Stylized astronaut / human subject icon matching the boxed sketch
        c.create_oval(26, 10, 48, 32, outline="#38bdf8", width=2)  # Helmet
        c.create_oval(30, 15, 44, 26, outline="#94a3b8", width=1)  # Visor
        c.create_line(37, 32, 37, 50, fill="#38bdf8", width=2)      # Torso
        c.create_line(22, 38, 52, 36, fill="#38bdf8", width=2)      # Arms
        c.create_line(37, 50, 26, 65, fill="#38bdf8", width=2)      # Left leg
        c.create_line(37, 50, 48, 63, fill="#38bdf8", width=2)      # Right leg

    def select_param(self, param_key):
        self.current_param = param_key
        self.refresh_ui()

    def select_layer(self, layer):
        self.current_layer = layer
        self.refresh_ui()

    def step_slide(self, delta):
        idx = PARAM_ORDER.index(self.current_param)
        new_idx = (idx + delta) % len(PARAM_ORDER)
        self.current_param = PARAM_ORDER[new_idx]
        self.refresh_ui()

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.attributes("-fullscreen", False)

    def update_telemetry(self, layer, param_key, value, status=None, status_color=None):
        """Public hook for live serial / socket telemetry streams."""
        entry = TELEMETRY_DATA[layer][param_key]
        entry["value"] = str(value)
        if status:
            entry["status"] = status
        if status_color:
            entry["status_color"] = status_color
        self.refresh_ui()

    def refresh_ui(self):
        layer_data = TELEMETRY_DATA[self.current_layer]

        # Update top pill buttons (HB | AMBIENT | EXTERNAL)
        for layer, lbl in self.layer_buttons.items():
            if layer == self.current_layer:
                lbl.configure(bg="#38bdf8", fg="#090d16")
            else:
                lbl.configure(bg="#131c2e", fg="#94a3b8")

        # Update left column parameter cubes
        for param_key, widgets in self.nav_cards.items():
            pdata = layer_data[param_key]
            is_active = param_key == self.current_param
            bg_color = "#1b2842" if is_active else "#131c2e"
            border_color = "#38bdf8" if is_active else "#2b3a55"
            title_color = "#38bdf8" if is_active else "#94a3b8"

            widgets["frame"].configure(bg=bg_color, highlightbackground=border_color)
            widgets["name"].configure(bg=bg_color, fg=title_color)
            widgets["value"].configure(
                bg=bg_color,
                text=f"{pdata['value']} {pdata['unit']}",
            )

        # Update active slide content
        active = layer_data[self.current_param]
        slide_num = PARAM_ORDER.index(self.current_param) + 1
        self.lbl_slide_counter.configure(text=f"SLIDE {slide_num} / {len(PARAM_ORDER)}  (↑ ↓)")

        self.lbl_hero_title.configure(text=active["title"])
        self.lbl_hero_value.configure(text=active["value"], fg=active["status_color"])
        self.lbl_hero_unit.configure(text=f" {active['unit']}")
        self.lbl_status_badge.configure(
            text=f"● {active['status']}  [{self.current_layer}]",
            fg=active["status_color"],
        )

        self.lbl_protocol_steps.configure(text="\n\n".join(active["protocol"]))
        rec_formatted = "\n\n".join(f"•  {item}" for item in active["recommendations"])
        self.lbl_recommendations.configure(text=rec_formatted)


if __name__ == "__main__":
    app = EgleTelemetrySlideApp()
    app.mainloop()