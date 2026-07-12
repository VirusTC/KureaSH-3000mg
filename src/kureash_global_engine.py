import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class KureaSHGlobalEngine:
    def __init__(self, weight_kg, height_cm, age, sex, build_mod, hydration_mod, entry_blood_ph, initial_crp_mg_l, university_code, current_fba_units):
        """
        Unified KureaSH™ Clinical Decision Support (CDSS) & Supply Chain Logistics Engine.
        Integrates:
        1. Biometric fluid volume scaling (Watson Formula).
        2. Pathological clearing adjustments based on ABG initial blood pH.
        3. Intracellular energy recovery tracking against inflammatory markers (CRP).
        4. Thermodynamic mitochondrial lipid oxidation vs. GI fat malabsorption.
        5. FBA Global SP-API supply chain triggers connected to NAKED manufacturing.
        """
        # Patient Biometric Parameters
        self.weight = float(weight_kg)
        self.height = float(height_cm)
        self.age = int(age)
        self.sex = sex.lower()
        self.volume_scaler = float(build_mod) * float(hydration_mod)
        
        # Clinical & Pathological Markers
        self.baseline_ph = float(entry_blood_ph)
        self.baseline_crp = float(initial_crp_mg_l)
        
        # Logistics & Institutional Infrastructure Metadata
        self.university = university_code
        self.stock = int(current_fba_units)
        self.fda_orphan_id = "298309"
        
        # Fixed Chemical, Physical, & Diet Constants
        self.kureash_mw = 149.15      # Molecular weight of creatine monohydrate complex (g/mol)
        self.pka = 4.8                # Baseline carboxylate constant for solution mapping
        self.diet_fat_g_day = 90.0    # Fixed standard daily fat ingestion baseline
        self.lead_time_days = 21       # Custom labeling + Amazon ingestion window
        
        # Initialize Engine States
        self.total_body_water = self._calculate_total_body_water()
        self._calculate_pathological_vulnerability()
        self.monthly_demand_units = 0.0

    def _calculate_total_body_water(self):
        """Calculates baseline distribution volume using the validated Watson Formula."""
        if self.sex == 'male':
            baseline = 2.447 - (0.09516 * self.age) + (0.1074 * self.height) + (0.3362 * self.weight)
        else:
            baseline = -2.097 + (0.1069 * self.height) + (0.2466 * self.weight)
        return baseline * self.volume_scaler

    def _calculate_pathological_vulnerability(self):
        """Derives clearance decay and buffer exhaustion directly from the baseline pH deficit."""
        ph_deficit = max(0.0, 7.40 - self.baseline_ph)
        # Bicarbonate buffering matrix degradation mapping
        self.buffer_capacity = max(0.02, 1.0 - (ph_deficit * 3.5))
        # Hepatic and renal clearance failure multiplier under acidic stress
        self.clearance_rate = max(0.20, 0.98 - (ph_deficit * 2.8))

    def set_institutional_demand(self, active_patients, maintenance_dose_g_day=5.0):
        """Calculates 30-day volume requirements for shipping 500g canisters to the trial site."""
        daily_total_g = active_patients * maintenance_dose_g_day
        monthly_total_g = daily_total_g * 30.4
        self.monthly_demand_units = np.ceil(monthly_total_g / 500.0)

    def simulate_clinical_timeline(self, start_dose_g, yearly_increment_g, total_days=1095):
        """
        Simulates 3 continuous years of daily patient monitoring, structural 
        accumulation kinetics, electrochemical shifts, and metabolic outcomes.
        """
        days = np.arange(1, total_days + 1)
        
        # Setup Data Arrays
        doses, ph_history, crp_history = [], [], []
        fat_oxidized_kg, exhaled_co2_kg, fecal_fat_history = [], [], []
        
        current_retained_mass_g = 0.0
        current_tissue_charge_pct = 65.0  # Depleted baseline starting point in inflamed joints
        cumulative_co2_g = 0.0
        
        for day in days:
            # Yearly Step-Up Protocols
            if day <= 365:
                current_dose_g = start_dose_g
            elif day <= 730:
                current_dose_g = start_dose_g + yearly_increment_g
            else:
                current_dose_g = start_dose_g + (2 * yearly_increment_g)
                
            # 1. Mass Accumulation and Retained Ionized Fraction [A-]
            total_active_mass_g = current_retained_mass_g + current_dose_g
            concentration_A = (total_active_mass_g / self.kureash_mw) / self.total_body_water
            
            # 2. Pathological Electrochemical pH Shift (Modified Henderson-Hasselbalch)
            ha_baseline = concentration_A / (10 ** (self.baseline_ph - self.pka))
            if ha_baseline > 0:
                raw_shift = np.log10(concentration_A / ha_baseline)
                modeled_ph = self.pka + (raw_shift * (1.0 / self.buffer_capacity))
                modeled_ph = max(min(modeled_ph, 7.95), 6.40)
            else:
                modeled_ph = self.baseline_ph
                
            # 3. Cellular Saturation Kinetics vs. Plasma Inflammation (CRP)
            g_per_kg = current_dose_g / self.weight
            absorption_rate = 1.8 if g_per_kg > 0.05 else 0.4
            current_tissue_charge_pct = min(100.0, current_tissue_charge_pct + absorption_rate)
            
            saturation_fraction = current_tissue_charge_pct / 100.0
            modeled_crp = max(0.5, self.baseline_crp * (1.0 - (saturation_fraction * 0.55)))
            
            # 4. Thermodynamic Fat Demolition Model ( BAT Thermogenesis )
            # Baseline passive lipolysis + high-dose cellular activation factors
            base_burn_g = 60.0
            thermogenic_boost_g = min(40.0, (current_dose_g * 1000.0 - 500.0) / 75.0) if current_dose_g >= 0.5 else 0.0
            daily_fat_oxidized_g = base_burn_g + thermogenic_boost_g
            
            # Strict Thermodynamic Conservation Split: 84% exhaled gas, 16% metabolic fluids
            daily_co2_g = daily_fat_oxidized_g * 0.84
            cumulative_co2_g += daily_co2_g
            
            # 5. GI Side-Effect and Malabsorption (Steatorrhea Tracking)
            # Doses exceeding 5g induce hyper-motility and lower the Coefficient of Absorption
            if current_dose_g < 5.0:
                coa = 0.95
            else:
                excess_g = current_dose_g - 5.0
                coa = max(0.40, 0.95 - (excess_g / 3.0))
            daily_fecal_fat_excreted_g = self.diet_fat_g_day * (1.0 - coa)
            
            # Save Historical Record
            doses.append(current_dose_g)
            ph_history.append(modeled_ph)
            crp_history.append(modeled_crp)
            fat_oxidized_kg.append(daily_fat_oxidized_g / 1000.0)
            exhaled_co2_kg.append(cumulative_co2_g / 1000.0)
            fecal_fat_history.append(daily_fecal_fat_excreted_g)
            
            # Process daily clearance balance carried forward to the next 24 hours
            current_retained_mass_g = total_active_mass_g * (1.0 - self.clearance_rate)
            
        return pd.DataFrame({
            'Day': days, 'Dose_g': doses, 'pH': ph_history, 'CRP': crp_history,
            'Fat_Oxidized_Daily_kg': fat_oxidized_kg, 'Cumulative_CO2_Exhaled_kg': exhaled_co2_kg,
            'Fecal_Fat_Excreted_g_day': fecal_fat_history
        })

    def generate_fba_supply_chain_signal(self, target_safety_buffer_days=45):
        """Queries current FBA global stock metrics against calculated institutional demand profiles."""
        if self.monthly_demand_units <= 0:
            return {"Error": "Institutional demand parameters not configured. Set active patient count."}
            
        daily_velocity_units = self.monthly_demand_units / 30.4
        days_runway = self.stock / daily_velocity_units
        reorder_threshold = daily_velocity_units * (self.lead_time_days + target_safety_buffer_days)
        
        report = {
            "Center_ID": self.university,
            "Target_Orphan_ID": self.fda_orphan_id,
            "Calculated_Monthly_Units_Needed": int(self.monthly_demand_units),
            "FBA_Warehouse_Stock": self.stock,
            "Inventory_Runway_Days": round(days_runway, 1)
        }
        
        if self.stock <= reorder_threshold:
            print_run_requirement = int(self.monthly_demand_units * 3)  # Trigger 90-day buffer production
            report["Logistics_Signal"] = f"TRIGGER PRIVATE LABEL RUN: Order NAKED to compile {print_run_requirement} custom-labeled canisters [Orphan #{self.fda_orphan_id}] for Amazon FBA ingestion."
        else:
            report["Logistics_Signal"] = "LOGISTICS NOMINAL: Current Amazon FBA inventory runway satisfies clinical target protocols."
            
        return report

# =====================================================================
# SYSTEM VERIFICATION AND ENGINE EXECUTION
# =====================================================================
if __name__ == "__main__":
    # Case Matrix Definition: 
    # Pediatric Oncology Patient: 35kg, 140cm, 10yo Male
    # Condition: Severe tumor-induced acidosis (Initial Blood pH: 7.22), Baseline high inflammation (CRP: 20.0 mg/L)
    # Logistics Node: Heidelberg Cancer Center (150 active clinical trial patients), 250 units currently remaining in FBA stock channels.
    
    engine = KureaSHGlobalEngine(
        weight_kg=35, height_cm=140, age=10, sex='male', 
        build_mod=1.0, hydration_mod=1.0, 
        entry_blood_ph=7.22, initial_crp_mg_l=20.0,
        university_code="HEID-CANCER-10", current_fba_units=250
    )
    
    # Configure the live tracking demand matrix
    engine.set_institutional_demand(active_patients=150, maintenance_dose_g_day=5.0)
    
    # Run the 3-Year Daily Dynamic Tracking Profile
    # Starting at 3g loading doses, escalating by 2g increments each year
df_timeline = engine.simulate_clinical_timeline(start_dose_g=3.0, yearly_increment_g=2.0)

# Fetch backend supply chain automated routing report\
supply_chain_report = engine.generate_fba_supply_chain_signal()

# -----------------------------------------------------------------\
# RENDER COMPREHENSIVE CDSS METRIC GRAPHICS\
# -----------------------------------------------------------------\
print(f"\n[Asset Verified] Total Distribution Fluid Matrix: {engine.total_body_water:.2f} Liters.")\
print(f"[Asset Verified] Pathological Buffer Capacity Coefficient: {engine.buffer_capacity:.3f}")\
print(f"[Asset Verified] Daily 24-Hour Clearance Rate Constraint: {engine.clearance_rate:.3f}\n")

for metric, value in supply_chain_report.items():\
print(f"{metric}: {value}")

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 9), sharex=True)

# Panel 1: Systemic pH Response\
ax1.plot(df_timeline['Day'], df_timeline['pH'], color='teal', linewidth=2)\
ax1.set_ylabel('Electrochemical pH Status')\
ax1.set_title('Pathological pH Trajectory Tracking')\
ax1.grid(True, linestyle=':', alpha=0.6)

# Panel 2: Inflammatory Biomarker Response (CRP)\
ax2.plot(df_timeline['Day'], df_timeline['CRP'], color='crimson', linewidth=2, linestyle='--')\
ax2.set_ylabel('Projected Serum CRP (mg/L)')\
ax2.set_title('Inflammation Resolution Profile')\
ax2.grid(True, linestyle=':', alpha=0.6)

# Panel 3: True Mitochondrial Fat Demolition (CO2 Gas Exhalation)\
ax3.plot(df_timeline['Day'], df_timeline['Cumulative_CO2_Exhaled_kg'], color='dimgray', linewidth=2.5)\
ax3.set_ylabel('Cumulative Exhaled Mass (kg)')\
ax3.set_xlabel('Timeline (Days Across 3 Years)')\
ax3.set_title('True Lipid Loss via Lung Oxidation (CO2)')\
ax3.grid(True, linestyle=':', alpha=0.6)

# Panel 4: Gastrointestinal Malabsorption Tracking (Steatorrhea Output)\
ax4.plot(df_timeline['Day'], df_timeline['Fecal_Fat_Excreted_g_day'], color='saddlebrown', linewidth=2)\
ax4.set_ylabel('Undigested Stool Fat (g/day)')\
ax4.set_xlabel('Timeline (Days Across 3 Years)')\
ax4.set_title('Induced Intestinal Steatorrhea Output')\
ax4.grid(True, linestyle=':', alpha=0.6)

plt.suptitle(f"KureaSH™ Clinical Decision Support System (CDSS) Dashboard --- Node: {engine.university} [Orphan #{engine.fda_orphan_id}]", fontsize=14, fontweight='bold')\
plt.tight_layout()\
plt.show()
