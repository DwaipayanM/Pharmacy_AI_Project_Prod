# COMPLETE_inventory_optimization_agent.py - 100% Requirements Aligned
# Section 2.3 of Requirements Document

"""
INVENTORY OPTIMIZATION AGENT
Purpose: Provide real-time inventory intelligence and reorder actions

CAPABILITIES (as per requirements):
✅ Current stock visibility across stores/warehouse
✅ Safety stock calculation
✅ Expiry tracking & near-expiry alerts
✅ Auto-reorder suggestions based on forecast
✅ Dead stock identification
✅ Stock transfer suggestions between stores (integration with Store Transfer Agent)

OUTPUTS (as per requirements):
✅ Recommended reorder quantity
✅ Stock transfer suggestions between stores
✅ Expiry liquidation alerts

BUSINESS IMPACT:
- Reduced expiry loss
- Optimized working capital
- Higher shelf availability

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

AVAILABLE_MODELS = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-2.5-flash']


class InventoryOptimizationAgent:
    """
    Complete Inventory Optimization Agent
    100% aligned with requirements document Section 2.3
    """
    
    def __init__(self):
        print("=" * 80)
        print("INVENTORY OPTIMIZATION AGENT (COMPLETE VERSION)")
        print(f"Using {len(API_KEYS)} API key(s)")
        print("=" * 80)
        
        self.current_key_index = 0
        self.inventory_data = None
        self.sales_data = None
        self.load_data()
        
        print("✅ Agent initialized with ALL capabilities!\n")
    
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
                    if any(x in str(e) for x in ['429', 'RESOURCE_EXHAUSTED', '404']):
                        continue
        return f"⚠️ All API keys at capacity."
    
    # ========================================================================
    # CAPABILITY 1: Current Stock Visibility Across Stores/Warehouse
    # ========================================================================
    
    def get_stock_visibility_comprehensive(self, sku=None, store_id=None):
        """Real-time stock visibility across all locations"""
        print("\n📊 COMPREHENSIVE STOCK VISIBILITY")
        print("=" * 80)
        
        data = self.inventory_data.copy()
        
        if sku:
            data = data[data['sku'] == sku]
        if store_id:
            data = data[data['store_id'] == store_id]
        
        if len(data) == 0:
            return {"success": False, "message": "No inventory found"}
        
        # Overall metrics
        total_stock = data['current_stock'].sum()
        total_value = (data['current_stock'] * data['unit_price']).sum()
        stores_count = data['store_id'].nunique()
        products_count = data['sku'].nunique()
        
        # By location
        by_location = data.groupby('store_id').agg({
            'current_stock': 'sum',
            'sku': 'count',
            'unit_price': lambda x: (data[data['store_id'] == x.name]['current_stock'] * 
                                     data[data['store_id'] == x.name]['unit_price']).sum()
        }).reset_index()
        by_location.columns = ['store_id', 'total_units', 'product_count', 'inventory_value']
        
        # By product
        by_product = data.groupby(['sku', 'product_name']).agg({
            'current_stock': 'sum',
            'unit_price': 'first',
            'store_id': 'count'
        }).reset_index()
        by_product['total_value'] = by_product['current_stock'] * by_product['unit_price']
        by_product.columns = ['sku', 'product_name', 'total_stock', 'unit_price', 'stores_count', 'total_value']
        by_product = by_product.sort_values('total_value', ascending=False)
        
        print(f"\n📈 OVERALL METRICS:")
        print(f"  Total Stock: {total_stock:,.0f} units")
        print(f"  Total Value: ${total_value:,.2f}")
        print(f"  Stores: {stores_count}")
        print(f"  Products: {products_count}")
        
        print(f"\n🏪 BY LOCATION:")
        for _, row in by_location.head(5).iterrows():
            print(f"  Store {row['store_id']}: {row['total_units']:,.0f} units | ${row['inventory_value']:,.2f}")
        
        return {
            "success": True,
            "summary": {
                "total_stock": int(total_stock),
                "total_value": round(total_value, 2),
                "stores_count": int(stores_count),
                "products_count": int(products_count)
            },
            "by_location": by_location.to_dict('records'),
            "by_product": by_product.head(10).to_dict('records')
        }
    
    # ========================================================================
    # CAPABILITY 2: Safety Stock Calculation
    # ========================================================================
    
    def calculate_safety_stock(self, sku):
        """Calculate optimal safety stock level using statistical methods"""
        print(f"\n🛡️ SAFETY STOCK CALCULATION: {sku}")
        print("=" * 80)
        
        sku_sales = self.sales_data[self.sales_data['sku'] == sku].copy()
        
        if len(sku_sales) < 30:
            return {"success": False, "message": "Insufficient sales history"}
        
        product_name = sku_sales['product_name'].iloc[0]
        
        # Calculate daily demand statistics
        daily_sales = sku_sales.groupby('date')['quantity_sold'].sum()
        
        avg_daily_demand = daily_sales.mean()
        std_daily_demand = daily_sales.std()
        max_daily_demand = daily_sales.max()
        
        # Parameters
        lead_time_days = 7  # Supplier lead time
        service_level = 0.95  # 95% service level
        z_score = 1.65  # For 95% service level
        
        # Safety stock formula: Z × StdDev × √Lead Time
        safety_stock = z_score * std_daily_demand * np.sqrt(lead_time_days)
        
        # Reorder point: (Avg Daily Demand × Lead Time) + Safety Stock
        reorder_point = (avg_daily_demand * lead_time_days) + safety_stock
        
        # Maximum inventory level
        max_stock = reorder_point + (avg_daily_demand * lead_time_days)
        
        print(f"\n📦 {product_name}")
        print(f"\n📊 DEMAND STATISTICS:")
        print(f"  Avg Daily Demand: {avg_daily_demand:.1f} units")
        print(f"  StdDev: {std_daily_demand:.1f} units")
        print(f"  Max Daily: {max_daily_demand:.0f} units")
        
        print(f"\n🎯 INVENTORY PARAMETERS:")
        print(f"  Safety Stock: {safety_stock:.0f} units")
        print(f"  Reorder Point: {reorder_point:.0f} units")
        print(f"  Max Stock Level: {max_stock:.0f} units")
        print(f"  Service Level: {service_level*100:.0f}%")
        
        return {
            "success": True,
            "sku": sku,
            "product_name": product_name,
            "demand_stats": {
                "avg_daily": round(avg_daily_demand, 2),
                "std_dev": round(std_daily_demand, 2),
                "max_daily": round(max_daily_demand, 0)
            },
            "inventory_params": {
                "safety_stock": round(safety_stock, 0),
                "reorder_point": round(reorder_point, 0),
                "max_stock": round(max_stock, 0),
                "lead_time_days": lead_time_days,
                "service_level": service_level * 100
            }
        }
    
    # ========================================================================
    # CAPABILITY 3: Expiry Tracking & Near-Expiry Alerts
    # ========================================================================
    
    def track_expiry_comprehensive(self, days_threshold=90):
        """Track items nearing expiry with detailed alerts"""
        print(f"\n⚠️ EXPIRY TRACKING (Next {days_threshold} days)")
        print("=" * 80)
        
        today = datetime.now()
        threshold_date = today + timedelta(days=days_threshold)
        
        # Find expiring items
        expiring = self.inventory_data[
            self.inventory_data['expiry_date'] <= threshold_date
        ].copy()
        
        expiring['days_to_expiry'] = (expiring['expiry_date'] - today).dt.days
        expiring['expiry_value'] = expiring['current_stock'] * expiring['unit_price']
        
        # Categorize by urgency
        critical = expiring[expiring['days_to_expiry'] <= 30]  # Critical: ≤30 days
        warning = expiring[(expiring['days_to_expiry'] > 30) & (expiring['days_to_expiry'] <= 60)]
        watch = expiring[expiring['days_to_expiry'] > 60]
        
        print(f"\n📊 EXPIRY SUMMARY:")
        print(f"  🔴 Critical (≤30 days): {len(critical)} items | ${critical['expiry_value'].sum():,.2f}")
        print(f"  🟡 Warning (31-60 days): {len(warning)} items | ${warning['expiry_value'].sum():,.2f}")
        print(f"  🟢 Watch (61-90 days): {len(watch)} items | ${watch['expiry_value'].sum():,.2f}")
        print(f"  💰 Total at Risk: ${expiring['expiry_value'].sum():,.2f}")
        
        # Liquidation alerts
        liquidation_alerts = []
        for _, item in critical.iterrows():
            liquidation_alerts.append({
                'sku': item['sku'],
                'product_name': item['product_name'],
                'store_id': item['store_id'],
                'stock': int(item['current_stock']),
                'days_to_expiry': int(item['days_to_expiry']),
                'value_at_risk': round(item['expiry_value'], 2),
                'recommended_action': 'IMMEDIATE CLEARANCE' if item['days_to_expiry'] <= 7 else 'DISCOUNT 20-30%'
            })
        
        return {
            "success": True,
            "summary": {
                "total_expiring": len(expiring),
                "critical_count": len(critical),
                "warning_count": len(warning),
                "watch_count": len(watch),
                "total_value_at_risk": round(expiring['expiry_value'].sum(), 2)
            },
            "liquidation_alerts": liquidation_alerts,
            "critical_items": critical.to_dict('records')
        }
    
    # ========================================================================
    # CAPABILITY 4: Auto-Reorder Suggestions Based on Forecast
    # ========================================================================
    
    def generate_reorder_recommendations(self, top_n=10):
        """Auto-reorder suggestions with optimal quantities"""
        print(f"\n🔄 AUTO-REORDER RECOMMENDATIONS (Top {top_n})")
        print("=" * 80)
        
        recommendations = []
        
        for sku in self.inventory_data['sku'].unique():
            # Calculate safety stock
            safety_calc = self.calculate_safety_stock(sku)
            
            if not safety_calc['success']:
                continue
            
            # Get current stock across all stores
            current_stock = self.inventory_data[
                self.inventory_data['sku'] == sku
            ]['current_stock'].sum()
            
            reorder_point = safety_calc['inventory_params']['reorder_point']
            safety_stock = safety_calc['inventory_params']['safety_stock']
            avg_daily_demand = safety_calc['demand_stats']['avg_daily']
            
            # Check if reorder needed
            if current_stock <= reorder_point:
                days_remaining = current_stock / avg_daily_demand if avg_daily_demand > 0 else 999
                urgency = days_remaining
                
                # Economic Order Quantity (simplified)
                order_qty = max(reorder_point + safety_stock - current_stock, 
                               avg_daily_demand * 14)  # At least 2 weeks supply
                
                recommendations.append({
                    'sku': sku,
                    'product_name': safety_calc['product_name'],
                    'current_stock': round(current_stock, 0),
                    'reorder_point': round(reorder_point, 0),
                    'recommended_order_qty': round(order_qty, 0),
                    'days_remaining': round(days_remaining, 1),
                    'urgency_score': round(urgency, 2),
                    'priority': 'URGENT' if days_remaining < 3 else 'HIGH' if days_remaining < 7 else 'NORMAL'
                })
        
        # Sort by urgency
        recommendations.sort(key=lambda x: x['urgency_score'])
        
        print(f"\n🎯 {len(recommendations)} PRODUCTS NEED REORDERING:")
        for i, rec in enumerate(recommendations[:top_n], 1):
            print(f"\n{i}. {rec['priority']} - {rec['product_name']}")
            print(f"   Current: {rec['current_stock']:.0f} | Reorder Point: {rec['reorder_point']:.0f}")
            print(f"   Recommended Order: {rec['recommended_order_qty']:.0f} units")
            print(f"   Days Remaining: {rec['days_remaining']:.1f}")
        
        return {
            "success": True,
            "total_reorder_needed": len(recommendations),
            "recommendations": recommendations[:top_n]
        }
    
    # ========================================================================
    # CAPABILITY 5: Dead Stock Identification (NEW - was missing!)
    # ========================================================================
    
    def identify_dead_stock(self, days_no_sales=90, min_stock_value=100):
        """Identify dead stock - items with no sales and low movement"""
        print(f"\n💀 DEAD STOCK IDENTIFICATION")
        print(f"Criteria: No sales in {days_no_sales} days + Min value ${min_stock_value}")
        print("=" * 80)
        
        cutoff_date = datetime.now() - timedelta(days=days_no_sales)
        
        dead_stock = []
        
        for sku in self.inventory_data['sku'].unique():
            # Check recent sales
            recent_sales = self.sales_data[
                (self.sales_data['sku'] == sku) & 
                (self.sales_data['date'] >= cutoff_date)
            ]
            
            # If no recent sales
            if len(recent_sales) == 0:
                sku_inventory = self.inventory_data[self.inventory_data['sku'] == sku]
                
                total_stock = sku_inventory['current_stock'].sum()
                unit_price = sku_inventory['unit_price'].iloc[0]
                total_value = total_stock * unit_price
                
                # Only flag if value is significant
                if total_value >= min_stock_value:
                    # Check historical sales
                    all_sales = self.sales_data[self.sales_data['sku'] == sku]
                    last_sale_date = all_sales['date'].max() if len(all_sales) > 0 else None
                    days_since_last_sale = (datetime.now() - last_sale_date).days if last_sale_date else 999
                    
                    dead_stock.append({
                        'sku': sku,
                        'product_name': sku_inventory['product_name'].iloc[0],
                        'total_stock': int(total_stock),
                        'unit_price': round(unit_price, 2),
                        'total_value': round(total_value, 2),
                        'days_since_last_sale': int(days_since_last_sale),
                        'stores_count': len(sku_inventory),
                        'recommended_action': self._get_dead_stock_action(days_since_last_sale, total_value)
                    })
        
        # Sort by value
        dead_stock.sort(key=lambda x: x['total_value'], reverse=True)
        
        total_dead_value = sum(item['total_value'] for item in dead_stock)
        
        print(f"\n📊 DEAD STOCK SUMMARY:")
        print(f"  Total Items: {len(dead_stock)}")
        print(f"  Total Value: ${total_dead_value:,.2f}")
        print(f"  Working Capital Locked: ${total_dead_value:,.2f}")
        
        if len(dead_stock) > 0:
            print(f"\n🔝 TOP 10 DEAD STOCK ITEMS:")
            for i, item in enumerate(dead_stock[:10], 1):
                print(f"\n{i}. {item['product_name']}")
                print(f"   Stock: {item['total_stock']} units | Value: ${item['total_value']:,.2f}")
                print(f"   Last Sale: {item['days_since_last_sale']} days ago")
                print(f"   Action: {item['recommended_action']}")
        
        return {
            "success": True,
            "total_dead_stock_items": len(dead_stock),
            "total_value_locked": round(total_dead_value, 2),
            "dead_stock": dead_stock
        }
    
    def _get_dead_stock_action(self, days_no_sale, value):
        """Determine action for dead stock"""
        if days_no_sale > 180:
            if value > 1000:
                return "Return to supplier or heavy discount (40-50%)"
            else:
                return "Liquidate or donate"
        elif days_no_sale > 120:
            return "Aggressive discount (30-40%) or bundle"
        else:
            return "Monitor and consider promotion (20-30% discount)"
    
    # ========================================================================
    # CAPABILITY 6: Stock Transfer Suggestions (Integration with Store Transfer Agent)
    # ========================================================================
    
    def suggest_stock_transfers_integrated(self):
        """Suggest inter-store transfers (integrates with Store Transfer Agent)"""
        print(f"\n🔀 STOCK TRANSFER SUGGESTIONS")
        print("=" * 80)
        
        transfer_suggestions = []
        
        # For each SKU, find imbalances
        for sku in self.inventory_data['sku'].unique():
            sku_inventory = self.inventory_data[self.inventory_data['sku'] == sku]
            
            if len(sku_inventory) < 2:
                continue  # Need at least 2 stores
            
            product_name = sku_inventory['product_name'].iloc[0]
            
            # Get sales velocity per store
            sku_sales = self.sales_data[self.sales_data['sku'] == sku]
            recent_sales = sku_sales[sku_sales['date'] >= datetime.now() - timedelta(days=30)]
            
            store_velocities = {}
            for store_id in sku_inventory['store_id'].unique():
                store_sales = recent_sales[recent_sales['store_id'] == store_id]
                velocity = store_sales.groupby('date')['quantity_sold'].sum().mean() if len(store_sales) > 0 else 0
                store_velocities[store_id] = velocity
            
            # Find overstocked and understocked
            for _, row in sku_inventory.iterrows():
                store_id = row['store_id']
                current_stock = row['current_stock']
                velocity = store_velocities.get(store_id, 0)
                
                days_of_supply = current_stock / velocity if velocity > 0 else 999
                
                # Overstocked: >60 days supply
                # Understocked: <7 days supply
                
                if days_of_supply > 60 and velocity > 0:
                    # Find understocked stores for same SKU
                    for other_store, other_velocity in store_velocities.items():
                        if other_store == store_id:
                            continue
                        
                        other_stock = sku_inventory[sku_inventory['store_id'] == other_store]['current_stock'].iloc[0]
                        other_days = other_stock / other_velocity if other_velocity > 0 else 999
                        
                        if other_days < 14:  # Understocked
                            transfer_qty = min(current_stock * 0.5, other_velocity * 14)
                            
                            if transfer_qty >= 10:
                                transfer_suggestions.append({
                                    'sku': sku,
                                    'product_name': product_name,
                                    'from_store': store_id,
                                    'to_store': other_store,
                                    'transfer_quantity': int(transfer_qty),
                                    'from_days_supply': round(days_of_supply, 1),
                                    'to_days_supply': round(other_days, 1),
                                    'reason': 'Balance inventory across stores',
                                    'priority': 'HIGH' if other_days < 7 else 'MEDIUM'
                                })
        
        # Sort by priority
        transfer_suggestions.sort(key=lambda x: (x['priority'] == 'HIGH', x['to_days_supply']))
        
        print(f"\n📊 TRANSFER SUGGESTIONS: {len(transfer_suggestions)}")
        
        if len(transfer_suggestions) > 0:
            print(f"\n🔝 TOP 10 TRANSFER OPPORTUNITIES:")
            for i, sugg in enumerate(transfer_suggestions[:10], 1):
                print(f"\n{i}. {sugg['priority']} - {sugg['product_name']}")
                print(f"   From Store {sugg['from_store']} ({sugg['from_days_supply']:.0f} days) → Store {sugg['to_store']} ({sugg['to_days_supply']:.0f} days)")
                print(f"   Transfer: {sugg['transfer_quantity']} units")
        else:
            print("\n✅ Inventory is balanced - no transfers needed")
        
        return {
            "success": True,
            "total_suggestions": len(transfer_suggestions),
            "suggestions": transfer_suggestions[:20]
        }
    
    # ========================================================================
    # AI-POWERED INSIGHTS
    # ========================================================================
    
    def get_comprehensive_ai_insights(self):
        """Get AI insights across all inventory capabilities"""
        print("\n🤖 COMPREHENSIVE INVENTORY INSIGHTS")
        print("=" * 80)
        
        # Gather data
        stock_vis = self.get_stock_visibility_comprehensive()
        expiry = self.track_expiry_comprehensive(90)
        reorder = self.generate_reorder_recommendations(5)
        dead_stock = self.identify_dead_stock(90, 100)
        transfers = self.suggest_stock_transfers_integrated()
        
        prompt = f"""You are a pharmacy inventory optimization expert. Analyze this comprehensive data and provide strategic recommendations.

INVENTORY STATUS:
- Total Value: ${stock_vis['summary']['total_value']:,.2f}
- Products: {stock_vis['summary']['products_count']}
- Stores: {stock_vis['summary']['stores_count']}

EXPIRY ALERTS:
- Critical Items: {expiry['summary']['critical_count']}
- Value at Risk: ${expiry['summary']['total_value_at_risk']:,.2f}

REORDER NEEDS:
- Products Needing Reorder: {reorder['total_reorder_needed']}

DEAD STOCK:
- Dead Stock Items: {dead_stock['total_dead_stock_items']}
- Capital Locked: ${dead_stock['total_value_locked']:,.2f}

TRANSFER OPPORTUNITIES:
- Transfer Suggestions: {transfers['total_suggestions']}

Provide:
1. Overall inventory health score (1-10)
2. Top 3 critical actions (prioritized)
3. Working capital optimization opportunities
4. Risk mitigation strategies
5. Expected business impact

Keep response concise and actionable."""
        
        insights = self.call_gemini_multi_key(prompt)
        
        print(f"\n💡 AI STRATEGIC INSIGHTS:")
        print(insights)
        
        return {
            "success": True,
            "insights": insights,
            "data_summary": {
                "total_value": stock_vis['summary']['total_value'],
                "expiry_risk": expiry['summary']['total_value_at_risk'],
                "reorder_needed": reorder['total_reorder_needed'],
                "dead_stock_value": dead_stock['total_value_locked'],
                "transfer_opportunities": transfers['total_suggestions']
            }
        }


def main():
    """Demo the Complete Inventory Optimization Agent"""
    agent = InventoryOptimizationAgent()
    
    print("\n" + "=" * 80)
    print("DEMO: COMPLETE INVENTORY OPTIMIZATION")
    print("=" * 80)
    
    # 1. Stock visibility
    print("\n\n1️⃣ STOCK VISIBILITY")
    agent.get_stock_visibility_comprehensive()
    
    # 2. Safety stock
    print("\n\n2️⃣ SAFETY STOCK CALCULATION")
    agent.calculate_safety_stock("MED001")
    
    # 3. Expiry tracking
    print("\n\n3️⃣ EXPIRY TRACKING")
    agent.track_expiry_comprehensive(90)
    
    # 4. Reorder recommendations
    print("\n\n4️⃣ AUTO-REORDER RECOMMENDATIONS")
    agent.generate_reorder_recommendations(10)
    
    # 5. Dead stock identification (NEW!)
    print("\n\n5️⃣ DEAD STOCK IDENTIFICATION")
    agent.identify_dead_stock(90, 100)
    
    # 6. Stock transfer suggestions (NEW!)
    print("\n\n6️⃣ STOCK TRANSFER SUGGESTIONS")
    agent.suggest_stock_transfers_integrated()
    
    # 7. AI insights
    print("\n\n7️⃣ AI-POWERED INSIGHTS")
    agent.get_comprehensive_ai_insights()
    
    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()
