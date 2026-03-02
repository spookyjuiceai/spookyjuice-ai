#!/usr/bin/env python3
"""
SpookyJuice AI Customer Service Demo
Shows how the AI handles different types of customer interactions
"""

import asyncio
import json

class CustomerServiceDemo:
    """Demonstrate customer service capabilities"""
    
    def __init__(self):
        self.demo_scenarios = [
            {
                "name": "Hot Lead - Enterprise Client",
                "caller": "+15551234567", 
                "conversation": [
                    {"user": "Hi, we're a 500-person company looking for AI automation for our customer support. We have a budget of around $200K and need to implement something in the next 3 months."},
                    {"ai": "Excellent! That's exactly our specialty. With 500 employees, you're likely handling thousands of support tickets. Tell me about your current pain points - are you dealing with repetitive questions, long response times, or scaling challenges?"},
                    {"user": "All of the above. Our support team is overwhelmed and customers are frustrated with wait times."},
                    {"ai": "I completely understand. We've solved this exact problem for several enterprise clients. I'm immediately scheduling you for a priority consultation with Brian, and I'm sending you three relevant case studies from similar-sized companies. You'll have a proposal within 48 hours."}
                ],
                "expected_routing": "schedule_consultation",
                "expected_followup": ["immediate_email", "consultation_booking", "sms_followup"]
            },
            {
                "name": "Warm Prospect - SMB", 
                "caller": "+15559876543",
                "conversation": [
                    {"user": "We're a small business and heard about AI but don't really know what we need."},
                    {"ai": "Perfect! That's a great place to start. Many successful AI implementations begin with understanding your specific challenges. What's your biggest operational pain point right now?"},
                    {"user": "We spend too much time on manual data entry and customer follow-ups."},
                    {"ai": "Those are ideal automation targets! I'm sending you our 'AI for Small Business' guide and scheduling a free 30-minute consultation where Brian can show you exactly how AI could save you 10-20 hours per week."}
                ],
                "expected_routing": "send_portfolio", 
                "expected_followup": ["warm_nurture_email", "whatsapp_portfolio"]
            },
            {
                "name": "Support Request",
                "caller": "+15556789012",
                "conversation": [
                    {"user": "Hi, we're having issues with the AI system you built for us last month."},
                    {"ai": "I'm so sorry to hear that! Let me get you connected to priority support immediately. Can you briefly describe the issue you're experiencing?"},
                    {"user": "The system stopped responding to API calls yesterday evening."},
                    {"ai": "That's definitely urgent. I'm creating a priority support ticket and Brian will personally look at this within the hour. I'm also sending you direct access to our emergency support line."}
                ],
                "expected_routing": "technical_support",
                "expected_followup": ["immediate_support_escalation", "status_updates"]
            }
        ]
    
    async def run_demo(self):
        """Run customer service demonstration"""
        print("🤖 SPOOKYJUICE AI CUSTOMER SERVICE DEMO")
        print("=" * 45)
        print()
        
        for scenario in self.demo_scenarios:
            print(f"📞 SCENARIO: {scenario['name']}")
            print(f"📱 Caller: {scenario['caller']}")
            print("-" * 30)
            
            for turn in scenario['conversation']:
                if 'user' in turn:
                    print(f"👤 Customer: {turn['user']}")
                if 'ai' in turn:
                    print(f"🤖 SpookyJuice: {turn['ai']}")
                print()
            
            print(f"🎯 Routing Decision: {scenario['expected_routing']}")
            print(f"📧 Follow-up Sequence: {', '.join(scenario['expected_followup'])}")
            print("=" * 45)
            print()
    
    async def simulate_lead_qualification(self, scenario_name: str):
        """Simulate lead qualification for a specific scenario"""
        scenario = next(s for s in self.demo_scenarios if s['name'] == scenario_name)
        
        conversation_text = "\n".join([
            f"Customer: {turn.get('user', '')}" 
            for turn in scenario['conversation'] 
            if 'user' in turn
        ])
        
        print(f"🧠 LEAD QUALIFICATION ANALYSIS: {scenario_name}")
        print("-" * 40)
        print(f"Conversation Input: {conversation_text[:200]}...")
        print()
        print("AI Analysis:")
        print("- Project Type: AI Automation")
        print("- Budget Mentioned: Yes" if "budget" in conversation_text.lower() else "- Budget Mentioned: No")
        print("- Timeline: Urgent" if any(word in conversation_text.lower() for word in ['urgent', 'asap', 'quickly']) else "- Timeline: Standard")
        print("- Decision Authority: High" if "we" in conversation_text.lower() else "- Decision Authority: Unknown")
        print(f"- Lead Score: {85 if scenario['expected_routing'] == 'schedule_consultation' else 45}/100")
        print(f"- Routing: {scenario['expected_routing']}")

if __name__ == "__main__":
    demo = CustomerServiceDemo()
    asyncio.run(demo.run_demo())