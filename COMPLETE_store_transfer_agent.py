# store_transfer_optimization_agent.py - NEW AGENT
# Aligned 100% with Requirements Document Section 3.3

"""
STORE TRANSFER OPTIMIZATION AGENT
Purpose: Suggest inter-store stock movement before reordering

CAPABILITIES (as per requirements):
✅ Suggests inter-store stock movement before reordering
✅ Prevents expiry in low-selling stores
✅ Optimizes stock distribution across locations

BUSINESS IMPACT:
- Reduced wastage
- Improved stock utilization
- Lower reorder costs

COST: $0 (Uses FREE Gemini API)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Load ALL available API keys
API_KEYS = []
for i in range(1, 10):
    if i == 1:
        key = os.getenv("GEMINI_API_KEY")
    else:
        key = os.getenv(f"GEMINI_API_KEY_{i}")
    
    if key:
        API_KEYS.append(key)

if not API_KEYS:
    raise ValueError("No GEMINI_API_KEY found!")

AVAILABLE_MODELS = [
    'gemini-2.0-flash',
    'gemini-1.5-flash',
    'gemini-2.5-flash',
]


class StoreTransferOptimizationAgent:
    """
    Store Transfer Optimization Agent
    NEW - was completely missing from original implementation
    100% aligned with requirements document section 3.3
    """
    
    def __init__(self):
        print("=" * 80)
        print("STORE TRANSFER OPTIMIZATION AGENT")
        print(f"Using {len(API_KEYS)} API key(s)")
        print("=" * 80)
        
        self.current_key_index = 0
        self.inventory_data = None
        self.sales_data = None
        self.load_data()
        
        print("✅ Agent initialized!\n")
    
    def load_data(self):
        """Load inventory and sales data"""
        try:
            print("Loading data...")
            self.inventory_data = pd.read_csv("data/current_inventory.csv")
            self.inventory_data['expiry_date'] = pd.to_datetime(self.inventory_data['expiry_date'])
            print(f"  ✓ Loaded {len(self.inventory_data):,} inventory records")
            
            self.sales_data = pd.read_csv("data/sales_history.csv")
            self.sales_data['date'] = pd.to_datetime(self.sales_data['date'])
            print(f"  ✓ Loaded {len(self.sales_data):,} sales records")
            
        except FileNotFoundError:
            print("\n❌ ERROR: Data files not found!")
            print("Run: python generate_sample_data.py")
            raise
    
    def call_gemini_multi_key(self, prompt):
        """Try multiple API keys until one works"""
        for key_idx in range(len(API_KEYS)):
            api_key = API_KEYS[(self.current_key_index + key_idx) % len(API_KEYS)]
            client = genai.Client(api_key=api_key)
            
            for model_name in AVAILABLE_MODELS:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(temperature=0.7)
                    )
                    self.current_key_index = (self.current_key_index + key_idx) % len(API_KEYS)
                    return response.text
                except Exception as e:
                    error_str = str(e)
                    if any(x in error_str for x in ['429', 'RESOURCE_EXHAUSTED', '404', 'NOT_FOUND']):
                        continue
                    else:
                        continue
        
        return f"⚠️ All {len(API_KEYS)} API keys at capacity."
    
    def analyze_store_inventory_imbalance(self):
        """Identify products with inventory imbalance across stores"""
        print("\n⚖️ STORE INVENTORY IMBALANCE ANALYSIS")
        print("=" * 80)
        
        imbalances = []
        
        # Group by SKU
        for sku in self.inventory_data['sku'].unique():
            sku_inventory = self.inventory_data[self.inventory_data['sku'] == sku]
            
            if len(sku_inventory) < 2:
                continue  # Need at least 2 stores
            
            product_name = sku_inventory['product_name'].iloc[0]
            
            # Calculate sales velocity per store
            sku_sales = self.sales_data[self.sales_data['sku'] == sku]
            recent_sales = sku_sales[sku_sales['date'] >= datetime.now() - timedelta(days=30)]
            
            store_velocities = {}
            for store_id in sku_inventory['store_id'].unique():
                store_sales = recent_sales[recent_sales['store_id'] == store_id]
                daily_velocity = store_sales.groupby('date')['quantity_sold'].sum().mean() if len(store_sales) > 0 else 0
                store_velocities[store_id] = daily_velocity
            
            # Find overstocked and understocked stores
            for _, row in sku_inventory.iterrows():
                store_id = row['store_id']
                current_stock = row['current_stock']
                velocity = store_velocities.get(store_id, 0)
                days_to_expiry = (row['expiry_date'] - datetime.now()).days
                
                # Calculate days of supply
                days_of_supply = current_stock / velocity if velocity > 0 else 999
                
                # Identify imbalance
                if days_of_supply > days_to_expiry and days_to_expiry < 90:
                    # Overstocked - will expire before selling
                    imbalances.append({
                        'sku': sku,
                        'product_name': product_name,
                        'from_store': store_id,
                        'current_stock': int(current_stock),
                        'daily_velocity': round(velocity, 2),
                        'days_of_supply': round(days_of_supply, 1),
                        'days_to_expiry': int(days_to_expiry),
                        'issue': 'OVERSTOCKED',
                        'urgency': 'HIGH' if days_to_expiry < 30 else 'MEDIUM'
                    })
                elif days_of_supply < 7 and velocity > 0:
                    # Understocked - will stock out soon
                    imbalances.append({
                        'sku': sku,
                        'product_name': product_name,
                        'from_store': store_id,
                        'current_stock': int(current_stock),
                        'daily_velocity': round(velocity, 2),
                        'days_of_supply': round(days_of_supply, 1),
                        'days_to_expiry': int(days_to_expiry),
                        'issue': 'UNDERSTOCKED',
                        'urgency': 'HIGH' if days_of_supply < 3 else 'MEDIUM'
                    })
        
        # Sort by urgency
        imbalances.sort(key=lambda x: (x['urgency'] == 'HIGH', x['days_to_expiry']), reverse=True)
        
        print(f"\n📊 IMBALANCES DETECTED: {len(imbalances)}")
        
        overstocked = [i for i in imbalances if i['issue'] == 'OVERSTOCKED']
        understocked = [i for i in imbalances if i['issue'] == 'UNDERSTOCKED']
        
        print(f"  🔴 Overstocked: {len(overstocked)} (risk of expiry)")
        print(f"  🟡 Understocked: {len(understocked)} (risk of stockout)")
        
        return {
            "success": True,
            "total_imbalances": len(imbalances),
            "overstocked": overstocked,
            "understocked": understocked,
            "all_imbalances": imbalances
        }
    
    def recommend_inter_store_transfers(self):
        """
        CORE FUNCTION: Recommend optimal stock transfers between stores
        This prevents expiry and stockouts WITHOUT new orders
        """
        print("\n🔄 INTER-STORE TRANSFER RECOMMENDATIONS")
        print("=" * 80)
        
        imbalance_analysis = self.analyze_store_inventory_imbalance()
        
        overstocked = imbalance_analysis['overstocked']
        understocked = imbalance_analysis['understocked']
        
        transfer_recommendations = []
        
        # Match overstocked with understocked for same SKU
        for overstock_item in overstocked:
            sku = overstock_item['sku']
            from_store = overstock_item['from_store']
            available_stock = overstock_item['current_stock']
            days_to_expiry = overstock_item['days_to_expiry']
            
            # Find understocked stores for same SKU
            matching_understock = [u for u in understocked if u['sku'] == sku and u['from_store'] != from_store]
            
            for understock_item in matching_understock:
                to_store = understock_item['from_store']
                needed_stock = understock_item['daily_velocity'] * 14  # 2 weeks supply
                
                # Calculate optimal transfer quantity
                transfer_qty = min(
                    available_stock * 0.7,  # Max 70% of source stock
                    needed_stock,  # Enough to cover 2 weeks
                    understock_item['daily_velocity'] * days_to_expiry  # What can sell before expiry
                )
                
                if transfer_qty >= 10:  # Minimum transfer quantity
                    # Calculate savings
                    expiry_prevention_value = transfer_qty * overstock_item.get('unit_price', 20)
                    stockout_prevention_value = transfer_qty * understock_item.get('unit_price', 20)
                    
                    transfer_recommendations.append({
                        'sku': sku,
                        'product_name': overstock_item['product_name'],
                        'from_store': from_store,
                        'to_store': to_store,
                        'transfer_quantity': int(transfer_qty),
                        'reason': f"Prevent expiry at {from_store}, fulfill demand at {to_store}",
                        'urgency': 'HIGH' if days_to_expiry < 30 else 'MEDIUM',
                        'days_to_expiry': days_to_expiry,
                        'estimated_savings': round(expiry_prevention_value, 2),
                        'prevents': 'BOTH expiry AND stockout',
                        'timeline': '24-48 hours' if overstock_item['urgency'] == 'HIGH' else '3-5 days'
                    })
                    
                    # Reduce available stock for next iteration
                    available_stock -= transfer_qty
                    if available_stock < 10:
                        break
        
        # Sort by urgency and savings
        transfer_recommendations.sort(key=lambda x: (x['urgency'] == 'HIGH', x['estimated_savings']), reverse=True)
        
        # Calculate total impact
        total_transfers = len(transfer_recommendations)
        total_units = sum(t['transfer_quantity'] for t in transfer_recommendations)
        total_savings = sum(t['estimated_savings'] for t in transfer_recommendations)
        
        print(f"\n📊 TRANSFER SUMMARY:")
        print(f"  Total Recommended Transfers: {total_transfers}")
        print(f"  Total Units to Transfer: {total_units:,}")
        print(f"  Estimated Savings: ${total_savings:,.2f}")
        
        if total_transfers > 0:
            print(f"\n🔝 TOP 10 PRIORITY TRANSFERS:")
            for i, transfer in enumerate(transfer_recommendations[:10], 1):
                print(f"\n{i}. {transfer['urgency']} - {transfer['product_name']}")
                print(f"   From: Store {transfer['from_store']} → To: Store {transfer['to_store']}")
                print(f"   Quantity: {transfer['transfer_quantity']} units")
                print(f"   Savings: ${transfer['estimated_savings']:,.2f}")
                print(f"   Timeline: {transfer['timeline']}")
                print(f"   Reason: {transfer['reason']}")
        else:
            print("\n✅ No urgent transfers needed - inventory is balanced!")
        
        return {
            "success": True,
            "total_transfers": total_transfers,
            "total_units": total_units,
            "total_savings": round(total_savings, 2),
            "transfers": transfer_recommendations
        }
    
    def prevent_expiry_through_transfers(self, days_threshold=30):
        """Focus specifically on preventing expiry through store transfers"""
        print(f"\n⚠️ EXPIRY PREVENTION THROUGH TRANSFERS (Next {days_threshold} days)")
        print("=" * 80)
        
        # Find items expiring soon
        expiring_items = self.inventory_data[
            (self.inventory_data['expiry_date'] - datetime.now()).dt.days <= days_threshold
        ].copy()
        
        expiring_items['days_to_expiry'] = (expiring_items['expiry_date'] - datetime.now()).dt.days
        
        transfer_opportunities = []
        
        for _, item in expiring_items.iterrows():
            sku = item['sku']
            from_store = item['store_id']
            stock = item['current_stock']
            days_to_expiry = item['days_to_expiry']
            
            # Find stores with higher demand for same SKU
            sku_sales = self.sales_data[self.sales_data['sku'] == sku]
            recent_sales = sku_sales[sku_sales['date'] >= datetime.now() - timedelta(days=30)]
            
            store_demand = recent_sales.groupby('store_id')['quantity_sold'].sum().to_dict()
            
            # Find best target store
            best_target = None
            best_demand = 0
            
            for target_store, demand in store_demand.items():
                if target_store != from_store and demand > best_demand:
                    best_demand = demand
                    best_target = target_store
            
            if best_target and best_demand > stock:
                # Calculate transfer quantity
                transfer_qty = min(stock, best_demand * 0.5)
                
                if transfer_qty >= 5:
                    transfer_opportunities.append({
                        'sku': sku,
                        'product_name': item['product_name'],
                        'from_store': from_store,
                        'to_store': best_target,
                        'transfer_quantity': int(transfer_qty),
                        'days_to_expiry': int(days_to_expiry),
                        'target_demand': int(best_demand),
                        'urgency': 'CRITICAL' if days_to_expiry <= 7 else 'HIGH',
                        'value_saved': round(transfer_qty * item['unit_price'], 2)
                    })
        
        # Sort by urgency
        transfer_opportunities.sort(key=lambda x: x['days_to_expiry'])
        
        total_value_saved = sum(t['value_saved'] for t in transfer_opportunities)
        
        print(f"\n📊 EXPIRY PREVENTION OPPORTUNITIES: {len(transfer_opportunities)}")
        print(f"  Total Value at Risk: ${total_value_saved:,.2f}")
        
        if len(transfer_opportunities) > 0:
            print(f"\n🚨 URGENT TRANSFERS TO PREVENT EXPIRY:")
            for i, opp in enumerate(transfer_opportunities[:10], 1):
                print(f"\n{i}. {opp['urgency']} - {opp['product_name']}")
                print(f"   Expires in: {opp['days_to_expiry']} days")
                print(f"   Transfer: {opp['transfer_quantity']} units")
                print(f"   From Store {opp['from_store']} → Store {opp['to_store']}")
                print(f"   Value Saved: ${opp['value_saved']:,.2f}")
        
        return {
            "success": True,
            "opportunities": transfer_opportunities,
            "total_value_at_risk": round(total_value_saved, 2)
        }
    
    def get_ai_transfer_insights(self):
        """Get AI-powered transfer strategy insights"""
        print("\n🤖 AI-POWERED TRANSFER INSIGHTS")
        print("=" * 80)
        
        transfers = self.recommend_inter_store_transfers()
        expiry_prevention = self.prevent_expiry_through_transfers(30)
        
        prompt = f"""You are a pharmacy supply chain expert. Analyze these store transfer opportunities.

TRANSFER RECOMMENDATIONS:
- Total Recommended Transfers: {transfers['total_transfers']}
- Total Units to Transfer: {transfers['total_units']:,}
- Estimated Savings: ${transfers['total_savings']:,.2f}

EXPIRY PREVENTION:
- Opportunities: {len(expiry_prevention['opportunities'])}
- Value at Risk: ${expiry_prevention['total_value_at_risk']:,.2f}

Provide:
1. Overall transfer strategy assessment
2. Implementation priorities (which transfers first)
3. Logistics considerations
4. Risk mitigation strategies
5. Expected business impact

Keep response concise and actionable."""
        
        insights = self.call_gemini_multi_key(prompt)
        
        print(f"\n💡 STRATEGIC INSIGHTS:")
        print(insights)
        
        return {
            "success": True,
            "insights": insights
        }


def main():
    """Demo the Store Transfer Optimization Agent"""
    agent = StoreTransferOptimizationAgent()
    
    print("\n" + "=" * 80)
    print("DEMO: STORE TRANSFER OPTIMIZATION")
    print("=" * 80)
    
    # 1. Analyze inventory imbalance
    print("\n\n1️⃣ INVENTORY IMBALANCE ANALYSIS")
    agent.analyze_store_inventory_imbalance()
    
    # 2. Recommend inter-store transfers
    print("\n\n2️⃣ INTER-STORE TRANSFER RECOMMENDATIONS")
    agent.recommend_inter_store_transfers()
    
    # 3. Prevent expiry through transfers
    print("\n\n3️⃣ EXPIRY PREVENTION STRATEGY")
    agent.prevent_expiry_through_transfers(30)
    
    # 4. AI insights
    print("\n\n4️⃣ AI-POWERED INSIGHTS")
    agent.get_ai_transfer_insights()
    
    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()
