import numpy as np
import pandas as pd

class AmazonInventoryBridge:
    def __init__(self, current_fba_stock_units, lead_time_days=14):
        """
        Manages the electronic interface between FBA stock levels, 
        custom printing triggers, and the NAKED manufacturing pipeline.
        """
        self.stock = int(current_fba_stock_units)
        self.lead_time = int(lead_time_days)
        self.daily_burn_rate = 0.0
        
    def update_sales_metrics(self, past_7_days_sales_units):
        """Calculates rolling daily velocity to forecast stock depletion."""
        self.daily_burn_rate = float(past_7_days_sales_units) / 7.0
        
    def generate_supply_chain_signals(self, target_safety_stock_days=30):
        """
        Determines exactly when to trigger a custom label print order
        to prevent FBA stockouts.
        """
        if self.daily_burn_rate <= 0:
            return "HOLD: No active sales velocity detected."
            
        days_of_stock_remaining = self.stock / self.daily_burn_rate
        reorder_point_units = self.daily_burn_rate * (self.lead_time + target_safety_stock_days)
        
        print(f"--- FBA Supply Chain Status ---")
        print(f"Current FBA Active Inventory: {self.stock} units")
        print(f"Current Sales Velocity: {self.daily_burn_rate:.1f} units/day")
        print(f"Estimated Runway: {days_of_stock_remaining:.1f} days")
        
        if self.stock <= reorder_point_units:
            units_to_order = int(self.daily_burn_rate * 60) # Order a 60-day supply
            return f"TRIGGER PRINT ORDER: Contact NAKED to print and ship {units_to_order} custom-labeled units to FBA."
        
        return "STATUS NORMAL: FBA inventory levels within safe threshold bounds."

# Quick verification run
if __name__ == "__main__":
    # Example: 450 units left in Amazon warehouses, selling 140 units a week
    bridge = AmazonInventoryBridge(current_fba_stock_units=450, lead_time_days=14)
    bridge.update_sales_metrics(past_7_days_sales_units=140)
    signal = bridge.generate_supply_chain_signals()
    print(f"Automation Output Signal: {signal}")
