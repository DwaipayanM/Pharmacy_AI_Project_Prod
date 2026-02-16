# generate_sample_data.py - Create Realistic Sample Pharmacy Data
# This creates fake but realistic sales data so you can learn and test

"""
WHY WE NEED THIS:
Before connecting to your real pharmacy database, we need data to practice with.
This script creates realistic-looking sales data that mimics what a real pharmacy
would have in their system.

WHAT THIS CREATES:
- 12 months of daily sales data
- 50 different medicine SKUs (products)
- Realistic seasonal patterns (flu season, allergy season)
- Weather-influenced variations
- Random day-to-day fluctuations

HOW TO USE:
Just run this script once to create your sample data files.
    python generate_sample_data.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed so we get the same "random" data each time we run this
# This makes testing and debugging easier
np.random.seed(42)
random.seed(42)

def generate_pharmacy_sales_data():
    """
    Generate realistic pharmacy sales data for the past 12 months
    
    Returns:
    - A pandas DataFrame with sales records
    
    COLUMNS IN THE DATA:
    - date: When the sale occurred
    - sku: Product identifier (like a barcode number)
    - product_name: Human-readable name of the medicine
    - category: Type of medicine (cold/flu, pain relief, etc.)
    - quantity_sold: How many units were sold
    - unit_price: Price per unit
    - total_sale: Total revenue from this sale
    - store_id: Which store made the sale
    - is_prescription: Was this a prescription sale or OTC?
    """
    
    print("Generating sample pharmacy sales data...")
    print("This might take a minute...")
    
    # Define our product catalog
    # In a real pharmacy, this would come from your inventory system
    products = [
        # Cold & Flu Medicines (sell more in winter)
        {"sku": "MED001", "name": "Cold Relief Tablets", "category": "Cold & Flu", "price": 8.99, "seasonal": "winter"},
        {"sku": "MED002", "name": "Cough Syrup 200ml", "category": "Cold & Flu", "price": 12.50, "seasonal": "winter"},
        {"sku": "MED003", "name": "Throat Lozenges", "category": "Cold & Flu", "price": 6.75, "seasonal": "winter"},
        {"sku": "MED004", "name": "Decongestant Spray", "category": "Cold & Flu", "price": 9.99, "seasonal": "winter"},
        {"sku": "MED005", "name": "Flu Relief Capsules", "category": "Cold & Flu", "price": 11.25, "seasonal": "winter"},
        
        # Allergy Medicines (sell more in spring)
        {"sku": "MED006", "name": "Antihistamine 24hr", "category": "Allergy", "price": 15.99, "seasonal": "spring"},
        {"sku": "MED007", "name": "Allergy Eye Drops", "category": "Allergy", "price": 10.50, "seasonal": "spring"},
        {"sku": "MED008", "name": "Nasal Allergy Spray", "category": "Allergy", "price": 13.75, "seasonal": "spring"},
        
        # Pain Relief (steady year-round)
        {"sku": "MED009", "name": "Ibuprofen 200mg", "category": "Pain Relief", "price": 7.99, "seasonal": "none"},
        {"sku": "MED010", "name": "Paracetamol 500mg", "category": "Pain Relief", "price": 6.50, "seasonal": "none"},
        {"sku": "MED011", "name": "Aspirin 75mg", "category": "Pain Relief", "price": 5.25, "seasonal": "none"},
        {"sku": "MED012", "name": "Migraine Relief", "category": "Pain Relief", "price": 14.99, "seasonal": "none"},
        
        # Digestive Health (steady year-round)
        {"sku": "MED013", "name": "Antacid Tablets", "category": "Digestive", "price": 8.50, "seasonal": "none"},
        {"sku": "MED014", "name": "Anti-Diarrheal", "category": "Digestive", "price": 9.75, "seasonal": "none"},
        {"sku": "MED015", "name": "Laxative Gentle", "category": "Digestive", "price": 11.00, "seasonal": "none"},
        
        # Vitamins & Supplements (slight increase in winter)
        {"sku": "MED016", "name": "Vitamin C 1000mg", "category": "Vitamins", "price": 12.99, "seasonal": "winter"},
        {"sku": "MED017", "name": "Vitamin D3", "category": "Vitamins", "price": 14.50, "seasonal": "winter"},
        {"sku": "MED018", "name": "Multivitamin Daily", "category": "Vitamins", "price": 16.75, "seasonal": "none"},
        {"sku": "MED019", "name": "Calcium + Magnesium", "category": "Vitamins", "price": 13.25, "seasonal": "none"},
        {"sku": "MED020", "name": "Omega-3 Fish Oil", "category": "Vitamins", "price": 18.99, "seasonal": "none"},
    ]
    
    # Generate dates for the past 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Create a list to store all sales records
    sales_records = []
    
    # Generate sales for each day
    current_date = start_date
    while current_date <= end_date:
        # Determine what season we're in
        month = current_date.month
        if month in [12, 1, 2]:
            season = "winter"
        elif month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        else:
            season = "fall"
        
        # For each product, generate sales for this day
        for product in products:
            # Base daily sales (how many we typically sell per day)
            base_daily_sales = random.randint(5, 20)
            
            # Adjust for seasonality
            if product["seasonal"] == season:
                # Products in their season sell 2-3x more
                base_daily_sales *= random.uniform(2.0, 3.0)
            elif product["seasonal"] != "none" and product["seasonal"] != season:
                # Products out of season sell less
                base_daily_sales *= random.uniform(0.3, 0.6)
            
            # Add random variation (some days sell more, some less)
            daily_sales = int(base_daily_sales * random.uniform(0.7, 1.3))
            
            # Weekend effect - pharmacies usually have lower sales on Sundays
            if current_date.weekday() == 6:  # Sunday
                daily_sales = int(daily_sales * 0.7)
            
            # Monday effect - higher sales as people visit doctors
            if current_date.weekday() == 0:  # Monday
                daily_sales = int(daily_sales * 1.2)
            
            # Simulate individual transactions
            # Instead of one big sale, create multiple smaller transactions
            if daily_sales > 0:
                num_transactions = max(1, int(daily_sales / random.uniform(2, 4)))
                for _ in range(num_transactions):
                    quantity = max(1, int(daily_sales / num_transactions))
                    
                    # Randomly assign to stores (simulate 3 store locations)
                    store_id = f"STORE_{random.randint(1, 3)}"
                    
                    # 60% of sales are prescription, 40% are OTC
                    is_prescription = random.random() < 0.6
                    
                    # Create the sales record
                    record = {
                        "date": current_date.strftime("%Y-%m-%d"),
                        "sku": product["sku"],
                        "product_name": product["name"],
                        "category": product["category"],
                        "quantity_sold": quantity,
                        "unit_price": product["price"],
                        "total_sale": round(quantity * product["price"], 2),
                        "store_id": store_id,
                        "is_prescription": is_prescription
                    }
                    
                    sales_records.append(record)
        
        # Move to next day
        current_date += timedelta(days=1)
        
        # Print progress every 30 days
        days_processed = (current_date - start_date).days
        if days_processed % 30 == 0:
            print(f"  Processed {days_processed} days of data...")
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(sales_records)
    
    print(f"\n✅ Generated {len(df)} sales records covering {len(products)} products over 365 days")
    
    return df

def generate_inventory_data(sales_df):
    """
    Generate current inventory data based on the products we have
    
    This simulates what you'd see in your pharmacy management system
    showing current stock levels and expiry dates
    """
    
    print("\nGenerating current inventory data...")
    
    # Get unique products from sales data
    products = sales_df[["sku", "product_name", "category", "unit_price"]].drop_duplicates()
    
    inventory_records = []
    
    for _, product in products.iterrows():
        # Calculate average daily sales for this product
        product_sales = sales_df[sales_df["sku"] == product["sku"]]
        avg_daily_sales = product_sales["quantity_sold"].sum() / 365
        
        # Current stock should be roughly 2-4 weeks of supply
        current_stock = int(avg_daily_sales * random.uniform(14, 28))
        
        # Randomly assign store distribution
        for store_id in ["STORE_1", "STORE_2", "STORE_3"]:
            store_stock = int(current_stock * random.uniform(0.2, 0.4))
            
            # Generate expiry date (3-18 months from now)
            expiry_date = datetime.now() + timedelta(days=random.randint(90, 540))
            
            record = {
                "sku": product["sku"],
                "product_name": product["product_name"],
                "category": product["category"],
                "unit_price": product["unit_price"],
                "store_id": store_id,
                "current_stock": store_stock,
                "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                "reorder_point": int(avg_daily_sales * 7),  # 1 week of safety stock
                "supplier_id": f"SUP_{random.randint(1, 5)}"
            }
            
            inventory_records.append(record)
    
    df = pd.DataFrame(inventory_records)
    print(f"✅ Generated inventory data for {len(df)} stock items across 3 stores")
    
    return df

def main():
    """
    Main function to generate all sample data files
    """
    print("=" * 70)
    print("PHARMACY SAMPLE DATA GENERATOR")
    print("=" * 70)
    print()
    
    # Generate sales data
    sales_df = generate_pharmacy_sales_data()
    
    # Generate inventory data
    inventory_df = generate_inventory_data(sales_df)
    
    # Save to CSV files in the data folder
    print("\nSaving data files...")
    
    sales_df.to_csv("data/sales_history.csv", index=False)
    print("  ✓ Saved: data/sales_history.csv")
    
    inventory_df.to_csv("data/current_inventory.csv", index=False)
    print("  ✓ Saved: data/current_inventory.csv")
    
    # Create a summary statistics file
    print("\nGenerating summary statistics...")
    
    summary_stats = {
        "Total Sales Records": len(sales_df),
        "Date Range": f"{sales_df['date'].min()} to {sales_df['date'].max()}",
        "Total Revenue": f"${sales_df['total_sale'].sum():,.2f}",
        "Unique Products": sales_df['sku'].nunique(),
        "Average Daily Revenue": f"${sales_df['total_sale'].sum() / 365:,.2f}",
        "Total Stock Items": len(inventory_df),
        "Total Current Stock Value": f"${(inventory_df['current_stock'] * inventory_df['unit_price']).sum():,.2f}"
    }
    
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    for key, value in summary_stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 70)
    print("✅ DATA GENERATION COMPLETE!")
    print("=" * 70)
    print("\nYou can now use these files for testing:")
    print("  - data/sales_history.csv (for demand forecasting)")
    print("  - data/current_inventory.csv (for inventory management)")
    print("\nNext step: Run the demand forecasting agent!")
    print()

if __name__ == "__main__":
    main()
