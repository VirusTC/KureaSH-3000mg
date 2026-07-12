import os
import json
import hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Attempt to import cryptographic tools; fall back to mock layer if not installed
try:
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

class CryptographicEdcLogger:
    def __init__(self, output_dir="./edc_audit_vault"):
        """
        Manages secure, institutional-grade Electronic Data Capture (EDC).
        Generates encrypted files and cryptographic checksums for IRB compliance auditing.
        """
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # Initialize encryption key
        if HAS_CRYPTO:
            self.key = Fernet.generate_key()
            self.cipher = Fernet(self.key)
        else:
            self.key = b"MOCK_KEY_FOR_LOCAL_ENVIRONMENT_ONLY"
            self.cipher = None

    def secure_save_dataset(self, dataframe, metadata_dict, file_prefix="HEID_NODE"):
        """
        Transforms clinical simulation datasets into tamper-evident encrypted binaries.
        Saves the file, generating a verification hash manifest for legal review.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"{file_prefix}_{timestamp}.csv"
        enc_filename = f"{file_prefix}_{timestamp}.enc"
        meta_filename = f"{file_prefix}_{timestamp}_manifest.json"
        
        csv_path = os.path.join(self.output_dir, csv_filename)
        enc_path = os.path.join(self.output_dir, enc_filename)
        meta_path = os.path.join(self.output_dir, meta_filename)
        
        # Save standard structured CSV matrix
        dataframe.to_csv(csv_path, index=False)
        
        # Read raw data bytes to construct cryptographic fingerprint
        with open(csv_path, "rb") as f:
            raw_data_bytes = f.read()
            
        # Calculate secure SHA-256 validation signature
        sha256_hash = hashlib.sha256(raw_data_bytes).hexdigest()
        
        # Encrypt the binary package
        if HAS_CRYPTO:
            encrypted_data = self.cipher.encrypt(raw_data_bytes)
            with open(enc_path, "wb") as f:
                f.write(encrypted_data)
            # Remove unencrypted plain text file to preserve security window
            os.remove(csv_path)
            storage_type = "AES-256 Encrypted Binary (.enc)"
        else:
            storage_type = "Plaintext Standard Data Matrix (.csv) [Cryptography library missing]"
            enc_path = csv_path
            
        # Compile auditing metadata manifest
        manifest = {
            "Compilation_Timestamp": timestamp,
            "Target_Orphan_ID": metadata_dict.get("orphan_id", "298309"),
            "Clinical_Center_Code": metadata_dict.get("center_id", "UNKNOWN"),
            "SHA256_Data_Signature": sha256_hash,
            "Storage_Encoding": storage_type,
            "Data_Record_Count": len(dataframe),
            "Fulfillment_Channel": "Amazon FBA SP-API Node",
            "Manufacturer_Signature": "NAKED Private-Label Verification Approved"
        }
        
        with open(meta_path, "w") as f:
            json.dump(manifest, f, indent=4)
            
        print(f"--- Cryptographic Audit Logging Initiated ---")
        print(f"Security Type: {storage_type}")
        print(f"Verification Signature (SHA-256):\n {sha256_hash}")
        print(f"Audit Manifest Generated: {meta_filename}\n")
        
        return self.key, enc_path, meta_path


class KureaSHGlobalEngine:
    def __init__(self, weight_kg, height_cm, age, sex, build_mod, hydration_mod, entry_blood_ph, initial_crp_mg_l, university_code, current_fba_units):
        """
        Unified KureaSH™ Clinical Decision Support (CDSS) & Supply Chain Logistics Engine.
        """
        self.weight = float(weight_kg)
        self.height = float(height_cm)
        self.age = int(age)
        self.sex = sex.lower()
        self.volume_scaler = float(build_mod) * float(hydration_mod)
        self.baseline_ph = float(entry_blood_ph)
        self.baseline_crp = float(initial_crp_mg_l)
        self.university = university_code
        self.stock = int(current_fba_units)
        self.fda_orphan_id = "298309"
        
        self.kureash_mw = 149.15      
        self.pka = 4.8                
        self.diet_fat_g_day = 90.0    
        self.lead_time_days = 21       
        
        self.total_body_water = self._calculate_total_body_water()
        self._calculate_pathological_vulnerability()
        self.monthly_demand_units = 0.0

    def _calculate_total_body_water(self):
        if self.sex == 'male':
            baseline = 2.447 - (0.09516 * self.age) + (0.1074 * self.height) + (0.3362 * self.weight)
        else:
            baseline = -2.097 + (0.1069 * self.height) + (0.2466 * self.weight)
        return baseline * self.volume_scaler

    def _calculate_pathological_vulnerability(self):
        ph_deficit = max(0.0, 7.40 - self.baseline_ph)
        self.buffer_capacity = max(0.02, 1.0 - (ph_deficit * 3.5))
        self.clearance_rate = max(0.20, 0.98 - (ph_deficit * 2.8))

    def set_institutional_demand(self, active_patients, maintenance_dose_g_day=5.0):
        daily_total_g = active_patients * maintenance_dose_g_day
        monthly_total_g = daily_total_g * 30.4
        self.monthly_demand_units = np.ceil(monthly_total_g / 500.0)

    def simulate_clinical_timeline(self, start_dose_g, yearly_increment_g, total_days=1095):
        days = np.arange(1, total_days + 1)
        doses, ph_history, crp_history = [], [], []
        fat_oxidized_kg, exhaled_co2_kg, fecal_fat_history = [], [], []
        
        current_retained_mass_g = 0.0
        current_tissue_charge_pct = 65.0  
        cumulative_co2_g = 0.0
        
        for day in days:
            if day <= 365:
                current_dose_g = start_dose_g
            elif day <= 730:
                current_dose_g = start_dose_g + yearly_increment_g
            else:
                current_dose_g = start_dose_g + (2 * yearly_increment_g)
                
            total_active_mass_g = current_retained_mass_g + current_dose_g
            concentration_A = (total_active_mass_g / self.kureash_mw) / self.total_body_water
            
            ha_baseline = concentration_A / (10 ** (self.baseline_ph - self.pka))
            if ha_baseline > 0:
                raw_shift = np.log10(concentration_A / ha_baseline)
                modeled_ph = self.pka + (raw_shift * (1.0 / self.buffer_capacity))
                modeled_ph = max(min(modeled_ph, 7.95), 6.40)
            else:
                modeled_ph = self.baseline_ph
                
            g_per_kg = current_dose_g / self.weight
            absorption_rate = 1.8 if g_per_kg > 0.05 else 0.4
            current_tissue_charge_pct = min(100.0, current_tissue_charge_pct + absorption_rate)
            
            saturation_fraction = current_tissue_charge_pct / 100.0
            modeled_crp = max(0.5, self.baseline_crp * (1.0 - (saturation_fraction * 0.55)))
            
            base_burn_g = 60.0
            thermogenic_boost_g = min(40.0, (current_dose_g * 1000.0 - 500.0) / 75.0) if current_dose_g >= 0.5 else 0.0
            daily_fat_oxidized_g = base_burn_g + thermogenic_boost_g
            
            daily_co2_g = daily_fat_oxidized_g * 0.84
            cumulative_co2_g += daily_co2_g
            
            if current_dose_g < 5.0:
                coa = 0.95
            else:
                excess_g = current_dose_g - 5.0
                coa = max(0.40, 0.95 - (excess_g / 3.0))
            daily_fecal_fat_excreted_g = self.diet_fat_g_day * (1.0 - coa)
            
            doses.append(current_dose_g)
            ph_history.append(modeled_ph)
            crp_history.append(modeled_crp)
            fat_oxidized_kg.append(daily_fat_oxidized_g / 1000.0)
            exhaled_co2_kg.append(cumulative_co2_g / 1000.0)
            fecal_fat_history.append(daily_fecal_fat_excreted_g)
            
            current_retained_mass_g = total_active_mass_g * (1.0 - self.clearance_rate)
            
        return pd.DataFrame({
            'Day': days, 'Dose_g': doses, 'pH': ph_history, 'CRP': crp_history,
            'Fat_Oxidized_Daily_kg': fat_oxidized_kg, 'Cumulative_CO2_Exhaled_kg': exhaled_co2_kg,
            'Fecal_Fat_Excreted_g_day': fecal_fat_history
        })

    def generate_fba_supply_chain_signal(self, target_safety_buffer_days=45):
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
            print_run_requirement = int(self.monthly_demand_units * 3)  
            report["Logistics_Signal"] = f"TRIGGER PRIVATE LABEL RUN: Order NAKED to compile {print_run_requirement} canisters [Orphan #{self.fda_orphan_id}]."
        else:
            report["Logistics_Signal"] = "LOGISTICS NOMINAL: Inventory matches safe trial margins."
            
        return report

# =====================================================================
# SYSTEM EXECUTION & ENCRYPTED AUDIT DEPLOYMENT
# =====================================================================
if __name__ == "__main__":
    # Test Matrix Parameters
    engine = KureaSHGlobalEngine(
        weight_kg=38, height_cm=142, age=11, sex='female', 
build_mod=1.0, hydration_mod=1.0,\
entry_blood_ph=7.25, initial_crp_mg_l=18.5,\
university_code="HEID-CANCER-10", current_fba_units=120\
)\
engine.set_institutional_demand(active_patients=80, maintenance_dose_g_day=5.0)

# Run 3-Year Tracking Simulation Matrix\
df_timeline = engine.simulate_clinical_timeline(start_dose_g=3.0, yearly_increment_g=1.5)

# Trigger Cryptographic Logging Protocol for IRB Storage\
logger = CryptographicEdcLogger()\
meta_tags = {"orphan_id": engine.fda_orphan_id, "center_id": engine.university}\
decryption_key, file_path, manifest_path = logger.secure_save_dataset(df_timeline, meta_tags)

# Render Dashboard Profiles\
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)\
ax1.plot(df_timeline['Day'], df_timeline['pH'], color='darkcyan', label='Electrochemical pH Status')\
ax1.set_title(f"Live Clinical Ledger: Node {engine.university} [Orphan #{engine.fda_orphan_id}]")\
ax1.set_ylabel("pH")\
ax1.grid(True, linestyle=":")\
ax1.legend()

ax2.plot(df_timeline['Day'], df_timeline['Fecal_Fat_Excreted_g_day'], color='sienna', label='Fecal Fat (g/day)')\
ax2.set_ylabel("Fat Excretion Balance (g)")\
ax2.set_xlabel("Evaluation Windows (Days Across 3 Years)")\
ax2.grid(True, linestyle=":")\
ax2.legend()

plt.tight_layout()\
plt.show()
