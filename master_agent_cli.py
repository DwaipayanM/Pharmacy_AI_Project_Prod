# master_agent_cli.py - Interactive Command Line Interface
# User-friendly CLI for the Master Agent

"""
PHARMACY AI - INTERACTIVE CLI

Features:
- Natural language questions
- Context-aware conversations
- Conversation history
- Detailed responses
- Agent consultation tracking

Usage:
    python master_agent_cli.py
"""

import sys
import os
from datetime import datetime
from master_agent import MasterAgent

# ANSI color codes for better CLI experience
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header():
    """Print welcome header"""
    print("\n" + "=" * 80)
    print(f"{Colors.BOLD}{Colors.CYAN}🏥 PHARMACY AI - MASTER AGENT{Colors.END}")
    print("=" * 80)
    print(f"{Colors.GREEN}Welcome to your intelligent pharmacy operations assistant!{Colors.END}")
    print()
    print("I can help you with:")
    print("  • Demand forecasting and sales predictions")
    print("  • Inventory optimization and reorder recommendations")
    print("  • Supplier selection and performance analysis")
    print("  • Pricing strategies and discount optimization")
    print("  • Store transfers and stock balancing")
    print("  • Working capital and budget planning")
    print("  • Prescription patterns and doctor analytics")
    print("  • Promotion effectiveness and ROI")
    print("  • Compliance monitoring and audit trails")
    print("  • Customer personalization and loyalty programs")
    print()
    print(f"{Colors.YELLOW}💡 Tips:{Colors.END}")
    print("  - Ask questions in natural language")
    print("  - I remember our conversation context")
    print("  - I'll show you which agents I consulted")
    print("  - Type 'help' for examples")
    print("  - Type 'history' to see conversation history")
    print("  - Type 'clear' to clear conversation history")
    print("  - Type 'exit' or 'quit' to leave")
    print("=" * 80 + "\n")

def print_help():
    """Print help with example questions"""
    print(f"\n{Colors.BOLD}📚 EXAMPLE QUESTIONS:{Colors.END}\n")
    
    examples = [
        ("Demand Forecasting", [
            "What will be demand for Paracetamol next month?",
            "Which products are fast-moving vs slow-moving?",
            "Predict demand for MED001 considering seasonal trends"
        ]),
        ("Inventory Management", [
            "What products are expiring in the next 30 days?",
            "Show me dead stock items with locked capital",
            "When should I reorder insulin?"
        ]),
        ("Supplier & Ordering", [
            "Which supplier should I use for 1000 units of Ibuprofen?",
            "Can I afford to order 2000 units at $25 each?",
            "Compare suppliers for reliability and pricing"
        ]),
        ("Pricing & Discounts", [
            "What discount should I offer on Vitamin C?",
            "Simulate margin impact for 15% discount on pain relievers",
            "Suggest clearance pricing for items expiring soon"
        ]),
        ("Store Operations", [
            "Should I transfer stock between stores?",
            "Which products are overstocked in Store A?",
            "How can I prevent expiry through store transfers?"
        ]),
        ("Multi-Agent Questions", [
            "I want to order 1000 Ibuprofen - which supplier, can I afford it, what price?",
            "Show me overstocked Vitamin C expiring in 20 days - transfer or discount?",
            "Analyze prescription trends and recommend targeted stocking"
        ])
    ]
    
    for category, questions in examples:
        print(f"{Colors.CYAN}• {category}:{Colors.END}")
        for q in questions:
            print(f"  - {q}")
        print()

def print_history(master):
    """Print conversation history"""
    history = master.get_conversation_history()
    
    if not history:
        print(f"\n{Colors.YELLOW}No conversation history yet.{Colors.END}\n")
        return
    
    print(f"\n{Colors.BOLD}📜 CONVERSATION HISTORY:{Colors.END}\n")
    
    for i, entry in enumerate(history, 1):
        timestamp = entry['timestamp'].strftime('%H:%M:%S')
        agents = ', '.join([a.capitalize() for a in entry['agents_consulted']])
        
        print(f"{Colors.CYAN}[{timestamp}] Question #{i}:{Colors.END}")
        print(f"  {entry['question']}")
        print(f"  {Colors.GREEN}→ Consulted: {agents}{Colors.END}")
        print()

def format_response(response):
    """Format the response with colors"""
    # Add colors to section headers
    response = response.replace('COMPREHENSIVE ANSWER', 
                               f"{Colors.BOLD}{Colors.GREEN}COMPREHENSIVE ANSWER{Colors.END}")
    response = response.replace('CONSULTATION DETAILS', 
                               f"{Colors.BOLD}{Colors.CYAN}CONSULTATION DETAILS{Colors.END}")
    
    # Highlight agent names
    for agent in ['Demand', 'Transfer', 'Supplier', 'Capital', 'Inventory', 
                  'Pricing', 'Prescription', 'Promotion', 'Compliance', 'Customer']:
        response = response.replace(f'{agent} Agent', 
                                   f"{Colors.YELLOW}{agent} Agent{Colors.END}")
    
    return response

def main():
    """Main CLI loop"""
    print_header()
    
    # Initialize Master Agent
    try:
        print(f"{Colors.YELLOW}Initializing Master Agent...{Colors.END}\n")
        master = MasterAgent()
        print(f"\n{Colors.GREEN}✓ Ready to answer your questions!{Colors.END}\n")
    except Exception as e:
        print(f"{Colors.RED}✗ Error initializing Master Agent: {e}{Colors.END}")
        print("\nPlease make sure:")
        print("  1. All agent files are in the same directory")
        print("  2. .env file exists with API keys")
        print("  3. Required libraries are installed")
        print("  4. Sample data exists in data/ folder\n")
        sys.exit(1)
    
    # Main conversation loop
    question_count = 0
    
    while True:
        try:
            # Get user input
            user_input = input(f"{Colors.BOLD}{Colors.BLUE}You:{Colors.END} ").strip()
            
            # Handle empty input
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print(f"\n{Colors.GREEN}Thank you for using Pharmacy AI!{Colors.END}")
                print(f"Session summary: {question_count} questions answered")
                print(f"Session duration: {datetime.now() - master.session_start}")
                print("\nGoodbye! 👋\n")
                break
            
            elif user_input.lower() == 'help':
                print_help()
                continue
            
            elif user_input.lower() == 'history':
                print_history(master)
                continue
            
            elif user_input.lower() == 'clear':
                master.clear_history()
                question_count = 0
                print(f"{Colors.GREEN}✓ Conversation history cleared{Colors.END}\n")
                continue
            
            elif user_input.lower() in ['?', 'commands']:
                print(f"\n{Colors.BOLD}Available commands:{Colors.END}")
                print("  help     - Show example questions")
                print("  history  - View conversation history")
                print("  clear    - Clear conversation history")
                print("  exit     - Exit the program\n")
                continue
            
            # Process the question
            question_count += 1
            
            print(f"\n{Colors.CYAN}Master Agent:{Colors.END} Processing your question...\n")
            
            try:
                response = master.ask(user_input)
                formatted_response = format_response(response)
                print(formatted_response)
                
            except Exception as e:
                print(f"{Colors.RED}Error processing question: {e}{Colors.END}")
                print("Please try rephrasing your question or type 'help' for examples.\n")
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Interrupted by user{Colors.END}")
            print(f"Type 'exit' to quit properly or continue asking questions.\n")
            continue
        
        except Exception as e:
            print(f"{Colors.RED}Unexpected error: {e}{Colors.END}")
            continue

if __name__ == "__main__":
    main()
