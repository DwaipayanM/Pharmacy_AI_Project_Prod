# master_agent.py - Master Agent Orchestrator
# Single entry point for all pharmacy AI agents

"""
MASTER AGENT - PHARMACY AI ORCHESTRATOR

This is the main interface for the Pharmacy AI Platform.
It automatically routes questions to the appropriate specialized agents
and synthesizes comprehensive responses.

Features:
- Natural language question processing
- Intelligent agent routing
- Multi-agent coordination
- Context-aware conversations
- Detailed explanations

Cost: $0 (Uses FREE Gemini API)
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Import all specialized agents
try:
    from COMPLETE_demand_forecasting_agent import DemandForecastingAgent
    from COMPLETE_store_transfer_agent import StoreTransferOptimizationAgent
    from COMPLETE_supplier_intelligence_agent import SupplierIntelligenceAgent
    from COMPLETE_working_capital_agent import WorkingCapitalAgent
    from COMPLETE_inventory_optimization_agent import InventoryOptimizationAgent
    from COMPLETE_discount_pricing_agent import DiscountPricingAgent
    from COMPLETE_prescription_intelligence_agent import PrescriptionIntelligenceAgent
    from COMPLETE_remaining_3_agents import PromotionEffectivenessAgent, ComplianceRegulationAgent, CustomerPersonalizationAgent
except ImportError as e:
    print(f"⚠️ Warning: Could not import some agents: {e}")
    print("Make sure all agent files are in the same directory.")

load_dotenv()

# Load API keys
API_KEYS = []
for i in range(1, 10):
    if i == 1:
        key = os.getenv("GEMINI_API_KEY")
    else:
        key = os.getenv(f"GEMINI_API_KEY_{i}")
    if key:
        API_KEYS.append(key)

AVAILABLE_MODELS = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-2.5-flash']


class MasterAgent:
    """
    Master Agent Orchestrator
    Routes questions to appropriate specialized agents
    """
    
    def __init__(self):
        print("\n" + "=" * 80)
        print("🏥 PHARMACY AI - MASTER AGENT INITIALIZING")
        print("=" * 80)
        
        self.current_key_index = 0
        self.conversation_history = []
        self.session_start = datetime.now()
        
        # Initialize all specialized agents
        print("\n📦 Loading specialized agents...")
        self.agents = {}
        
        try:
            print("  1. Demand Forecasting Agent...", end="")
            self.agents['demand'] = DemandForecastingAgent()
            print(" ✓")
        except Exception as e:
            print(f" ✗ ({e})")
        
        try:
            print("  2. Store Transfer Agent...", end="")
            self.agents['transfer'] = StoreTransferOptimizationAgent()
            print(" ✓")
        except Exception as e:
            print(f" ✗ ({e})")
        
        try:
            print("  3. Supplier Intelligence Agent...", end="")
            self.agents['supplier'] = SupplierIntelligenceAgent()
            print(" ✓")
        except Exception as e:
            print(f" ✗ ({e})")
        
        try:
            print("  4. Working Capital Agent...", end="")
            self.agents['capital'] = WorkingCapitalAgent()
            print(" ✓")
        except Exception as e:
            print(f" ✗ ({e})")
        
        try:
            print("  5. Inventory Optimization Agent...", end="")
            self.agents['inventory'] = InventoryOptimizationAgent()
            print(" ✓")
        except Exception as e:
            print(f" ✗ ({e})")
        
        try:
            print("  6. Discount & Pricing Agent...", end="")
            self.agents['pricing'] = DiscountPricingAgent()
            print(" ✓")
        except Exception as e:
            print(f" ✗ ({e})")
        
        try:
            print("  7. Prescription Intelligence Agent...", end="")
            self.agents['prescription'] = PrescriptionIntelligenceAgent()
            print(" ✓")
        except Exception as e:
            print(f" ✗ ({e})")
        
        try:
            print("  8. Promotion Effectiveness Agent...", end="")
            self.agents['promotion'] = PromotionEffectivenessAgent()
            print(" ✓")
        except Exception as e:
            print(f" ✗ ({e})")
        
        try:
            print("  9. Compliance & Regulation Agent...", end="")
            self.agents['compliance'] = ComplianceRegulationAgent()
            print(" ✓")
        except Exception as e:
            print(f" ✗ ({e})")
        
        try:
            print("  10. Customer Personalization Agent...", end="")
            self.agents['customer'] = CustomerPersonalizationAgent()
            print(" ✓")
        except Exception as e:
            print(f" ✗ ({e})")
        
        print(f"\n✅ Master Agent Ready! ({len(self.agents)}/10 agents loaded)")
        print("=" * 80 + "\n")
    
    def call_gemini_multi_key(self, prompt):
        """Call Gemini API with multi-key support"""
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
        return None
    
    def analyze_question(self, question):
        """
        Analyze the question to determine which agent(s) to consult
        Uses AI to intelligently route questions
        """
        # Build context from conversation history
        context = ""
        if len(self.conversation_history) > 0:
            context = "Previous conversation:\n"
            for entry in self.conversation_history[-3:]:  # Last 3 exchanges
                context += f"User: {entry['question']}\n"
                context += f"Answer: {entry['answer'][:200]}...\n\n"
        
        # AI-powered question analysis
        analysis_prompt = f"""You are a pharmacy operations expert analyzing user questions to route them to specialized agents.

{context}

Current question: "{question}"

Available agents:
1. demand - Demand forecasting, sales prediction, reorder timing
2. transfer - Inter-store transfers, inventory balancing, expiry prevention
3. supplier - Supplier selection, performance, split ordering, reliability
4. capital - Budget validation, working capital, cash flow, ROI
5. inventory - Stock levels, safety stock, dead stock, expiry tracking
6. pricing - Discounts, pricing strategy, margin simulation, competitor pricing
7. prescription - Doctor patterns, clinic demand, prescription forecasting
8. promotion - Campaign ROI, promotion effectiveness
9. compliance - Regulatory compliance, controlled drugs, audit trails
10. customer - Customer recommendations, loyalty, personalization

Analyze the question and determine:
1. Which agent(s) should handle this (list agent names separated by commas)
2. Key parameters to extract (SKU, quantity, timeframe, location, etc.)
3. Question type (single agent, multi-agent, clarification needed)

Respond in this exact format:
AGENTS: agent1, agent2, agent3
PARAMETERS: sku=MED001, days=30, quantity=1000
TYPE: single OR multi OR clarify
REASONING: Brief explanation

Be concise and precise."""

        ai_analysis = self.call_gemini_multi_key(analysis_prompt)
        
        if not ai_analysis:
            # Fallback to keyword-based routing
            return self.keyword_based_routing(question)
        
        # Parse AI response
        agents_to_consult = []
        parameters = {}
        question_type = "single"
        reasoning = ""
        
        for line in ai_analysis.split('\n'):
            if line.startswith('AGENTS:'):
                agents_str = line.replace('AGENTS:', '').strip()
                agents_to_consult = [a.strip() for a in agents_str.split(',') if a.strip()]
            elif line.startswith('PARAMETERS:'):
                params_str = line.replace('PARAMETERS:', '').strip()
                for param in params_str.split(','):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        parameters[key.strip()] = value.strip()
            elif line.startswith('TYPE:'):
                question_type = line.replace('TYPE:', '').strip().lower()
            elif line.startswith('REASONING:'):
                reasoning = line.replace('REASONING:', '').strip()
        
        return {
            'agents': agents_to_consult,
            'parameters': parameters,
            'type': question_type,
            'reasoning': reasoning
        }
    
    def keyword_based_routing(self, question):
        """Fallback keyword-based routing if AI analysis fails"""
        question_lower = question.lower()
        agents_to_consult = []
        
        # Keyword mappings
        if any(word in question_lower for word in ['demand', 'forecast', 'predict', 'future', 'next month', 'sales']):
            agents_to_consult.append('demand')
        
        if any(word in question_lower for word in ['transfer', 'move stock', 'between stores', 'relocate']):
            agents_to_consult.append('transfer')
        
        if any(word in question_lower for word in ['supplier', 'vendor', 'order from', 'purchase']):
            agents_to_consult.append('supplier')
        
        if any(word in question_lower for word in ['budget', 'afford', 'capital', 'cash flow', 'roi']):
            agents_to_consult.append('capital')
        
        if any(word in question_lower for word in ['inventory', 'stock', 'reorder', 'expiry', 'expiring', 'dead stock']):
            agents_to_consult.append('inventory')
        
        if any(word in question_lower for word in ['discount', 'price', 'pricing', 'margin', 'clearance']):
            agents_to_consult.append('pricing')
        
        if any(word in question_lower for word in ['prescription', 'doctor', 'clinic', 'prescrib']):
            agents_to_consult.append('prescription')
        
        if any(word in question_lower for word in ['promotion', 'campaign', 'marketing']):
            agents_to_consult.append('promotion')
        
        if any(word in question_lower for word in ['compliance', 'regulation', 'audit', 'controlled']):
            agents_to_consult.append('compliance')
        
        if any(word in question_lower for word in ['customer', 'loyalty', 'personalize', 'recommend']):
            agents_to_consult.append('customer')
        
        return {
            'agents': agents_to_consult if agents_to_consult else ['inventory'],  # Default to inventory
            'parameters': {},
            'type': 'single' if len(agents_to_consult) <= 1 else 'multi',
            'reasoning': 'Keyword-based routing (fallback)'
        }
    
    def consult_agents(self, agents_to_consult, parameters, question):
        """
        Consult the specified agents and collect their responses
        """
        results = {}
        
        for agent_name in agents_to_consult:
            if agent_name not in self.agents:
                results[agent_name] = {
                    'success': False,
                    'message': f'Agent {agent_name} not available'
                }
                continue
            
            try:
                agent = self.agents[agent_name]
                
                # Route to appropriate agent method based on agent type and parameters
                if agent_name == 'demand':
                    sku = parameters.get('sku', 'MED001')
                    days = int(parameters.get('days', '30'))
                    results[agent_name] = agent.forecast_with_external_factors(sku, days)
                
                elif agent_name == 'transfer':
                    results[agent_name] = agent.recommend_inter_store_transfers()
                
                elif agent_name == 'supplier':
                    sku = parameters.get('sku', 'MED001')
                    results[agent_name] = agent.recommend_supplier_for_sku(sku)
                
                elif agent_name == 'capital':
                    results[agent_name] = agent.calculate_current_inventory_value()
                
                elif agent_name == 'inventory':
                    if 'dead stock' in question.lower():
                        results[agent_name] = agent.identify_dead_stock(90, 100)
                    elif 'expir' in question.lower():
                        results[agent_name] = agent.track_expiry_comprehensive(90)
                    elif 'reorder' in question.lower():
                        results[agent_name] = agent.generate_reorder_recommendations(10)
                    else:
                        results[agent_name] = agent.get_stock_visibility_comprehensive()
                
                elif agent_name == 'pricing':
                    sku = parameters.get('sku', 'MED001')
                    results[agent_name] = agent.recommend_sku_discount_comprehensive(sku)
                
                elif agent_name == 'prescription':
                    location = parameters.get('location', None)
                    results[agent_name] = agent.analyze_doctor_prescribing_behavior(location)
                
                elif agent_name == 'promotion':
                    results[agent_name] = agent.measure_campaign_roi()
                
                elif agent_name == 'compliance':
                    results[agent_name] = agent.ensure_storage_compliance()
                
                elif agent_name == 'customer':
                    customer_id = parameters.get('customer_id', 'CUST0001')
                    results[agent_name] = agent.recommend_otc_products(customer_id)
                
            except Exception as e:
                results[agent_name] = {
                    'success': False,
                    'message': f'Error consulting {agent_name}: {str(e)}'
                }
        
        return results
    
    def synthesize_response(self, question, analysis, agent_results):
        """
        Synthesize a comprehensive response from multiple agent results
        """
        # Build context for AI synthesis
        context = f"""Question: {question}

Agents Consulted: {', '.join(analysis['agents'])}
Reasoning: {analysis['reasoning']}

Agent Results:
"""
        
        for agent_name, result in agent_results.items():
            context += f"\n{agent_name.upper()} AGENT:\n"
            context += str(result)[:500] + "...\n"
        
        # AI-powered synthesis
        synthesis_prompt = f"""{context}

You are a pharmacy operations expert. Based on the agent results above, provide a comprehensive, detailed answer to the user's question.

Requirements:
1. Start with a direct answer
2. Provide detailed explanation
3. Include specific numbers and recommendations
4. Mention which agents were consulted and what they found
5. Give actionable next steps
6. Be professional but conversational

Format your response clearly with sections if needed."""
        
        synthesized = self.call_gemini_multi_key(synthesis_prompt)
        
        if not synthesized:
            # Fallback: Simple concatenation
            response = f"Based on consultation with {', '.join(analysis['agents'])} agent(s):\n\n"
            for agent_name, result in agent_results.items():
                response += f"**{agent_name.upper()}:** "
                if isinstance(result, dict) and 'success' in result:
                    response += str(result.get('message', result))[:200] + "\n\n"
            return response
        
        return synthesized
    
    def ask(self, question):
        """
        Main method: Ask a question and get a comprehensive answer
        """
        print(f"\n{'='*80}")
        print(f"📝 QUESTION: {question}")
        print(f"{'='*80}\n")
        
        # Step 1: Analyze question
        print("🔍 Analyzing question...")
        analysis = self.analyze_question(question)
        
        print(f"   → Routing to: {', '.join(analysis['agents'])}")
        print(f"   → Type: {analysis['type']}")
        print(f"   → Reasoning: {analysis['reasoning']}\n")
        
        # Step 2: Consult agents
        print("🤖 Consulting specialized agents...")
        agent_results = self.consult_agents(analysis['agents'], analysis['parameters'], question)
        
        for agent_name in analysis['agents']:
            status = "✓" if agent_results.get(agent_name, {}).get('success', False) else "✗"
            print(f"   {status} {agent_name.capitalize()} Agent")
        
        print()
        
        # Step 3: Synthesize response
        print("💡 Synthesizing comprehensive response...\n")
        response = self.synthesize_response(question, analysis, agent_results)
        
        # Step 4: Add to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now(),
            'question': question,
            'answer': response,
            'agents_consulted': analysis['agents']
        })
        
        # Step 5: Format and return response
        formatted_response = f"""
{'='*80}
📊 COMPREHENSIVE ANSWER
{'='*80}

{response}

{'='*80}
🔧 CONSULTATION DETAILS
{'='*80}
Agents Consulted: {', '.join([a.capitalize() for a in analysis['agents']])}
Question Type: {analysis['type'].capitalize()}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}
"""
        
        return formatted_response
    
    def get_conversation_history(self):
        """Get conversation history for this session"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("✓ Conversation history cleared")


# Quick test
if __name__ == "__main__":
    print("Testing Master Agent...")
    
    try:
        master = MasterAgent()
        
        # Test question
        response = master.ask("What will be the demand for Paracetamol next month?")
        print(response)
        
    except Exception as e:
        print(f"Error: {e}")
