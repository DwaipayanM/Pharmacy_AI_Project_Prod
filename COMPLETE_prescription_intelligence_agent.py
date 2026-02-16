# COMPLETE_prescription_intelligence_agent.py - 100% Requirements Aligned
# Section 3.1 of Requirements Document

"""
PRESCRIPTION PATTERN INTELLIGENCE AGENT
Purpose: Analyze doctor prescribing behavior and predict demand

CAPABILITIES (as per requirements):
✅ Analyzes doctor prescribing behavior
✅ Predicts upcoming medicine demand by clinic/location
✅ Enables targeted stocking and promotions

BUSINESS IMPACT:
- Higher prescription fulfillment rate

COST: $0 (Uses FREE Gemini API)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from collections import Counter

load_dotenv()

API_KEYS = []
for i in range(1, 10):
    if i == 1:
        key = os.getenv("GEMINI_API_KEY")
    else:
        key = os.getenv(f"GEMINI_API_KEY_{i}")
    if key:
        API_KEYS.append(key)

AVAILABLE_MODELS = ['gemini-2.0-flash', 'gemini-1.5-flash']


class PrescriptionIntelligenceAgent:
    """
    Complete Prescription Intelligence Agent
    100% aligned with requirements Section 3.1
    """
    
    def __init__(self):
        print("=" * 80)
        print("PRESCRIPTION INTELLIGENCE AGENT (COMPLETE VERSION)")
        print(f"Using {len(API_KEYS)} API key(s)")
        print("=" * 80)
        
        self.current_key_index = 0
        self.create_prescription_data()
        
        print("✅ Agent initialized!\n")
    
    def create_prescription_data(self):
        """Create comprehensive prescription data with clinic/location details"""
        print("Creating prescription intelligence data...")
        
        np.random.seed(42)
        
        # Locations with clinics
        self.locations = {
            'Mumbai': ['Fortis Hospital', 'Apollo Clinic', 'Lilavati Hospital', 'KEM Hospital'],
            'Delhi': ['AIIMS', 'Max Hospital', 'Apollo Hospital', 'Safdarjung Hospital'],
            'Bangalore': ['Manipal Hospital', 'Columbia Asia', 'Narayana Health', 'St Johns'],
            'Pune': ['Ruby Hall', 'Sahyadri Hospital', 'Deenanath Hospital', 'Jehangir Hospital'],
            'Chennai': ['Apollo Chennai', 'MIOT Hospital', 'Fortis Malar', 'Kauvery Hospital']
        }
        
        # Doctors by specialty and location
        self.doctors_data = []
        doctor_id = 1
        
        for location, clinics in self.locations.items():
            for clinic in clinics:
                # Each clinic has 3-5 doctors
                num_doctors = np.random.randint(3, 6)
                for _ in range(num_doctors):
                    specialty = np.random.choice([
                        'General Physician', 'Cardiologist', 'Diabetologist',
                        'Orthopedic', 'Pediatrician', 'Dermatologist'
                    ])
                    
                    self.doctors_data.append({
                        'doctor_id': f'DR{doctor_id:03d}',
                        'doctor_name': f'Dr. {np.random.choice(["Sharma", "Patel", "Kumar", "Singh", "Reddy"])} {doctor_id}',
                        'specialty': specialty,
                        'clinic': clinic,
                        'location': location,
                        'patients_per_day': np.random.randint(15, 40),
                        'prescriptions_per_patient': np.random.uniform(1.5, 3.0),
                        'years_experience': np.random.randint(5, 30)
                    })
                    doctor_id += 1
        
        self.doctors_df = pd.DataFrame(self.doctors_data)
        
        # Prescription patterns by specialty
        self.specialty_patterns = {
            'General Physician': ['Paracetamol', 'Ibuprofen', 'Amoxicillin', 'Azithromycin'],
            'Cardiologist': ['Atorvastatin', 'Amlodipine', 'Aspirin', 'Metoprolol'],
            'Diabetologist': ['Metformin', 'Glimepiride', 'Insulin', 'Sitagliptin'],
            'Orthopedic': ['Diclofenac', 'Calcium', 'Vitamin D', 'Methylcobalamin'],
            'Pediatrician': ['Paracetamol Syrup', 'Amoxicillin', 'Cetirizine', 'ORS'],
            'Dermatologist': ['Cetaphil', 'Adapalene', 'Fluconazole', 'Hydrocortisone']
        }
        
        # Generate prescription records
        prescription_records = []
        
        for _ in range(2000):  # 2000 prescriptions
            doctor = self.doctors_df.sample(1).iloc[0]
            
            # Medicines based on specialty
            medicines = self.specialty_patterns.get(doctor['specialty'], ['Generic Medicine'])
            prescribed_medicine = np.random.choice(medicines)
            
            prescription_records.append({
                'prescription_id': f'RX{np.random.randint(10000, 99999)}',
                'date': datetime.now() - timedelta(days=np.random.randint(1, 90)),
                'doctor_id': doctor['doctor_id'],
                'doctor_name': doctor['doctor_name'],
                'specialty': doctor['specialty'],
                'clinic': doctor['clinic'],
                'location': doctor['location'],
                'medicine_prescribed': prescribed_medicine,
                'quantity': np.random.randint(10, 60),
                'patient_age_group': np.random.choice(['0-18', '19-35', '36-50', '51-65', '65+']),
                'chronic_condition': np.random.choice([True, False], p=[0.3, 0.7]),
                'refill_expected': np.random.choice([True, False], p=[0.4, 0.6])
            })
        
        self.prescription_df = pd.DataFrame(prescription_records)
        self.prescription_df['date'] = pd.to_datetime(self.prescription_df['date'])
        
        print(f"  ✓ Doctors: {len(self.doctors_df)}")
        print(f"  ✓ Clinics: {sum(len(clinics) for clinics in self.locations.values())}")
        print(f"  ✓ Locations: {len(self.locations)}")
        print(f"  ✓ Prescriptions: {len(self.prescription_df):,}")
    
    def call_gemini_multi_key(self, prompt):
        """Call Gemini API"""
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
                    return response.text
                except:
                    continue
        return "⚠️ API unavailable"
    
    # ========================================================================
    # CAPABILITY 1: Analyze Doctor Prescribing Behavior
    # ========================================================================
    
    def analyze_doctor_prescribing_behavior(self, location=None, specialty=None):
        """Comprehensive doctor prescribing analysis"""
        print("\n👨‍⚕️ DOCTOR PRESCRIBING BEHAVIOR ANALYSIS")
        print("=" * 80)
        
        # Filter data
        data = self.prescription_df.copy()
        if location:
            data = data[data['location'] == location]
        if specialty:
            data = data[data['specialty'] == specialty]
        
        # Top prescribing doctors
        doctor_stats = data.groupby(['doctor_id', 'doctor_name', 'specialty', 'clinic', 'location']).agg({
            'prescription_id': 'count',
            'medicine_prescribed': lambda x: x.mode()[0] if len(x.mode()) > 0 else None
        }).reset_index()
        doctor_stats.columns = ['doctor_id', 'doctor_name', 'specialty', 'clinic', 'location', 
                                'total_prescriptions', 'most_prescribed']
        doctor_stats = doctor_stats.sort_values('total_prescriptions', ascending=False)
        
        # Specialty patterns
        specialty_stats = data.groupby('specialty')['prescription_id'].count().sort_values(ascending=False)
        
        # Medicine patterns
        medicine_stats = data['medicine_prescribed'].value_counts().head(10)
        
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"  Total Prescriptions: {len(data):,}")
        print(f"  Doctors: {data['doctor_id'].nunique()}")
        print(f"  Clinics: {data['clinic'].nunique()}")
        
        print(f"\n🏆 TOP 5 PRESCRIBING DOCTORS:")
        for i, row in doctor_stats.head(5).iterrows():
            print(f"\n{i+1}. {row['doctor_name']} ({row['specialty']})")
            print(f"   Clinic: {row['clinic']}, {row['location']}")
            print(f"   Prescriptions: {row['total_prescriptions']}")
            print(f"   Most Prescribed: {row['most_prescribed']}")
        
        print(f"\n📋 TOP SPECIALTIES:")
        for specialty, count in specialty_stats.head(5).items():
            pct = (count / len(data)) * 100
            print(f"  {specialty}: {count} ({pct:.1f}%)")
        
        return {
            "success": True,
            "total_prescriptions": len(data),
            "doctor_stats": doctor_stats.to_dict('records'),
            "specialty_stats": specialty_stats.to_dict(),
            "medicine_stats": medicine_stats.to_dict()
        }
    
    # ========================================================================
    # CAPABILITY 2: Predict Upcoming Demand by Clinic/Location (NEW!)
    # ========================================================================
    
    def predict_demand_by_clinic_location(self, days_ahead=30):
        """Predict medicine demand by clinic and location"""
        print(f"\n📍 DEMAND PREDICTION BY CLINIC/LOCATION (Next {days_ahead} days)")
        print("=" * 80)
        
        predictions_by_location = []
        
        for location in self.locations.keys():
            location_data = self.prescription_df[self.prescription_df['location'] == location]
            
            # Calculate daily prescription rate
            days_of_data = (location_data['date'].max() - location_data['date'].min()).days
            daily_rx_rate = len(location_data) / days_of_data if days_of_data > 0 else 0
            
            # Predict for next N days
            predicted_prescriptions = daily_rx_rate * days_ahead
            
            # Top medicines by this location
            top_medicines = location_data['medicine_prescribed'].value_counts().head(5)
            
            predictions_by_location.append({
                'location': location,
                'current_daily_rx': round(daily_rx_rate, 1),
                'predicted_total_rx': round(predicted_prescriptions, 0),
                'top_medicines': top_medicines.to_dict(),
                'clinics_count': location_data['clinic'].nunique(),
                'doctors_count': location_data['doctor_id'].nunique()
            })
        
        # Sort by predicted volume
        predictions_by_location.sort(key=lambda x: x['predicted_total_rx'], reverse=True)
        
        # Predictions by clinic
        predictions_by_clinic = []
        
        for clinic in self.prescription_df['clinic'].unique():
            clinic_data = self.prescription_df[self.prescription_df['clinic'] == clinic]
            
            days_of_data = (clinic_data['date'].max() - clinic_data['date'].min()).days
            daily_rx_rate = len(clinic_data) / days_of_data if days_of_data > 0 else 0
            predicted_prescriptions = daily_rx_rate * days_ahead
            
            top_medicine = clinic_data['medicine_prescribed'].value_counts().iloc[0] if len(clinic_data) > 0 else None
            
            predictions_by_clinic.append({
                'clinic': clinic,
                'location': clinic_data['location'].iloc[0],
                'predicted_prescriptions': round(predicted_prescriptions, 0),
                'top_medicine': top_medicine,
                'doctors': clinic_data['doctor_id'].nunique()
            })
        
        predictions_by_clinic.sort(key=lambda x: x['predicted_prescriptions'], reverse=True)
        
        # Print results
        print(f"\n📍 BY LOCATION:")
        for pred in predictions_by_location:
            print(f"\n{pred['location']}:")
            print(f"  Predicted Rx: {pred['predicted_total_rx']:.0f} prescriptions")
            print(f"  Clinics: {pred['clinics_count']} | Doctors: {pred['doctors_count']}")
            print(f"  Top Medicines: {', '.join(list(pred['top_medicines'].keys())[:3])}")
        
        print(f"\n🏥 TOP 5 HIGH-VOLUME CLINICS:")
        for i, pred in enumerate(predictions_by_clinic[:5], 1):
            print(f"\n{i}. {pred['clinic']} ({pred['location']})")
            print(f"   Predicted Rx: {pred['predicted_prescriptions']:.0f}")
            print(f"   Top Medicine: {pred['top_medicine']}")
        
        return {
            "success": True,
            "by_location": predictions_by_location,
            "by_clinic": predictions_by_clinic
        }
    
    # ========================================================================
    # CAPABILITY 3: Targeted Stocking & Promotions (NEW!)
    # ========================================================================
    
    def generate_targeted_stocking_recommendations(self):
        """Generate location-specific stocking recommendations"""
        print("\n🎯 TARGETED STOCKING RECOMMENDATIONS")
        print("=" * 80)
        
        recommendations = []
        
        for location in self.locations.keys():
            location_rx = self.prescription_df[self.prescription_df['location'] == location]
            
            # Top 5 medicines for this location
            top_medicines = location_rx['medicine_prescribed'].value_counts().head(5)
            
            # Specialty distribution
            specialties = location_rx['specialty'].value_counts()
            top_specialty = specialties.iloc[0] if len(specialties) > 0 else None
            
            # Patient demographics
            age_groups = location_rx['patient_age_group'].value_counts()
            dominant_age_group = age_groups.iloc[0] if len(age_groups) > 0 else None
            
            # Chronic condition rate
            chronic_rate = location_rx['chronic_condition'].mean() * 100
            
            recommendations.append({
                'location': location,
                'priority_medicines': list(top_medicines.index),
                'stock_quantities': [int(count * 1.5) for count in top_medicines.values],  # 1.5x safety factor
                'dominant_specialty': specialties.index[0],
                'dominant_age_group': dominant_age_group,
                'chronic_condition_rate': round(chronic_rate, 1),
                'recommended_actions': self._get_location_actions(location, top_specialty, chronic_rate)
            })
        
        print(f"\n🎯 LOCATION-SPECIFIC RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"\n📍 {rec['location']}:")
            print(f"  Dominant Specialty: {rec['dominant_specialty']}")
            print(f"  Chronic Patients: {rec['chronic_condition_rate']:.0f}%")
            print(f"\n  Priority Stock:")
            for i, (medicine, qty) in enumerate(zip(rec['priority_medicines'][:3], rec['stock_quantities'][:3]), 1):
                print(f"    {i}. {medicine}: Stock {qty} units")
            print(f"\n  Actions: {rec['recommended_actions']}")
        
        return {
            "success": True,
            "recommendations": recommendations
        }
    
    def _get_location_actions(self, location, top_specialty, chronic_rate):
        """Generate specific actions for location"""
        actions = []
        
        if chronic_rate > 40:
            actions.append("Stock 30-day supplies for chronic medications")
        
        if top_specialty == 'Cardiologist':
            actions.append("Promote heart health supplements")
        elif top_specialty == 'Diabetologist':
            actions.append("Stock diabetic care products")
        elif top_specialty == 'Pediatrician':
            actions.append("Focus on children's medicines and vitamins")
        
        actions.append("Partner with local clinics for prescription fulfillment")
        
        return " | ".join(actions)
    
    # ========================================================================
    # AI-POWERED INSIGHTS
    # ========================================================================
    
    def get_ai_prescription_insights(self, location=None):
        """Get AI insights on prescription patterns"""
        print("\n🤖 AI-POWERED PRESCRIPTION INSIGHTS")
        print("=" * 80)
        
        analysis = self.analyze_doctor_prescribing_behavior(location)
        demand = self.predict_demand_by_clinic_location(30)
        stocking = self.generate_targeted_stocking_recommendations()
        
        location_filter = f" for {location}" if location else ""
        
        prompt = f"""You are a pharmacy prescription intelligence expert. Analyze these prescription patterns{location_filter}.

PRESCRIPTION STATISTICS:
- Total Prescriptions: {analysis['total_prescriptions']:,}
- Unique Doctors: {len(analysis['doctor_stats'])}
- Top Medicines: {', '.join(list(analysis['medicine_stats'].keys())[:5])}

LOCATION INSIGHTS:
- Locations: {len(demand['by_location'])}
- Top Location Demand: {demand['by_location'][0]['predicted_total_rx']:.0f} prescriptions/month

Provide:
1. Prescription pattern insights
2. Market opportunities by location
3. Doctor engagement strategies
4. Stock optimization recommendations
5. Revenue growth opportunities

Keep response concise."""
        
        insights = self.call_gemini_multi_key(prompt)
        
        print(f"\n💡 INSIGHTS:")
        print(insights)
        
        return {
            "success": True,
            "insights": insights
        }


def main():
    """Demo the Prescription Intelligence Agent"""
    agent = PrescriptionIntelligenceAgent()
    
    print("\n" + "=" * 80)
    print("DEMO: PRESCRIPTION INTELLIGENCE")
    print("=" * 80)
    
    # 1. Doctor prescribing behavior
    print("\n\n1️⃣ DOCTOR PRESCRIBING BEHAVIOR")
    agent.analyze_doctor_prescribing_behavior()
    
    # 2. Demand by clinic/location (NEW!)
    print("\n\n2️⃣ DEMAND PREDICTION BY CLINIC/LOCATION")
    agent.predict_demand_by_clinic_location(30)
    
    # 3. Targeted stocking (NEW!)
    print("\n\n3️⃣ TARGETED STOCKING RECOMMENDATIONS")
    agent.generate_targeted_stocking_recommendations()
    
    # 4. AI insights
    print("\n\n4️⃣ AI-POWERED INSIGHTS")
    agent.get_ai_prescription_insights("Mumbai")
    
    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()
