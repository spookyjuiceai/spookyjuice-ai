#!/usr/bin/env python3
"""
SpookyJuice AI - Intelligent Customer Service & Lead Qualification System
First line of defense for potential customers with smart routing and follow-up
"""

import os
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import openai
import requests
from flask import Flask, request, Response
import sqlite3
from security_framework import SecurityManager

class CustomerType(Enum):
    HOT_LEAD = "hot_lead"           # Ready to buy/hire
    WARM_PROSPECT = "warm_prospect"  # Interested, needs nurturing
    COLD_INQUIRY = "cold_inquiry"    # General questions
    EXISTING_CLIENT = "existing_client" # Current customer
    SUPPORT_REQUEST = "support_request" # Technical support
    SPAM_LIKELY = "spam_likely"      # Probably spam/sales

class RoutingAction(Enum):
    SCHEDULE_CONSULTATION = "schedule_consultation"
    SEND_TO_WHATSAPP = "send_to_whatsapp"
    COLLECT_REQUIREMENTS = "collect_requirements"
    TECHNICAL_SUPPORT = "technical_support"
    SEND_PORTFOLIO = "send_portfolio"
    SCHEDULE_DEMO = "schedule_demo"
    TAKE_MESSAGE = "take_message"
    POLITE_DECLINE = "polite_decline"

@dataclass
class CustomerProfile:
    phone_number: str
    name: Optional[str]
    company: Optional[str]
    project_type: Optional[str]
    budget_range: Optional[str]
    timeline: Optional[str]
    pain_points: List[str]
    lead_score: int
    customer_type: CustomerType
    conversation_summary: str
    next_action: RoutingAction
    created_at: datetime

class LeadQualificationAI:
    """Advanced AI for qualifying leads and determining routing"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Lead scoring criteria
        self.scoring_weights = {
            'budget_mentioned': 30,
            'timeline_urgent': 25,
            'specific_project': 20,
            'decision_maker': 15,
            'company_size': 10
        }
    
    async def qualify_lead(self, conversation_history: List[Dict], caller_info: Dict) -> CustomerProfile:
        """Qualify lead using advanced AI analysis"""
        
        # Combine all conversation text
        conversation_text = "\n".join([
            f"Caller: {turn.get('user', '')}\nSpookyJuice: {turn.get('ai', '')}"
            for turn in conversation_history
        ])
        
        qualification_prompt = f"""
        Analyze this customer service conversation to qualify the lead:
        
        Conversation:
        {conversation_text}
        
        Caller Phone: {caller_info.get('phone', 'unknown')}
        
        Extract and analyze:
        1. Customer Type (hot_lead, warm_prospect, cold_inquiry, existing_client, support_request, spam_likely)
        2. Project Details (type, scope, complexity)
        3. Budget Indicators (mentioned amounts, ranges, or implied budget)
        4. Timeline (urgency, specific dates, general timeframe)
        5. Decision Making Authority (are they the decision maker?)
        6. Pain Points (what problems are they trying to solve?)
        7. Company Information (size, industry, existing tech stack)
        8. Lead Score (0-100 based on buying intent and fit)
        9. Recommended Routing Action
        
        Return as JSON with detailed reasoning.
        """
        
        try:
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": qualification_prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # Create customer profile
            profile = CustomerProfile(
                phone_number=caller_info.get('phone', 'unknown'),
                name=analysis.get('customer_name'),
                company=analysis.get('company'),
                project_type=analysis.get('project_type'),
                budget_range=analysis.get('budget_range'),
                timeline=analysis.get('timeline'),
                pain_points=analysis.get('pain_points', []),
                lead_score=analysis.get('lead_score', 0),
                customer_type=CustomerType(analysis.get('customer_type', 'cold_inquiry')),
                conversation_summary=analysis.get('summary', ''),
                next_action=RoutingAction(analysis.get('recommended_action', 'take_message')),
                created_at=datetime.now()
            )
            
            return profile
            
        except Exception as e:
            print(f"Lead qualification error: {e}")
            # Default low-priority profile
            return CustomerProfile(
                phone_number=caller_info.get('phone', 'unknown'),
                name=None, company=None, project_type=None,
                budget_range=None, timeline=None, pain_points=[],
                lead_score=10, customer_type=CustomerType.COLD_INQUIRY,
                conversation_summary="Error during qualification",
                next_action=RoutingAction.TAKE_MESSAGE,
                created_at=datetime.now()
            )

class FollowUpOrchestrator:
    """Manages intelligent follow-up workflows across channels"""
    
    def __init__(self):
        self.channels = {
            'email': self.send_email,
            'sms': self.send_sms,
            'whatsapp': self.send_whatsapp,
            'calendar': self.schedule_meeting
        }
        
        # Follow-up sequences based on customer type
        self.sequences = {
            CustomerType.HOT_LEAD: [
                {'delay_hours': 0, 'channel': 'email', 'template': 'hot_lead_immediate'},
                {'delay_hours': 1, 'channel': 'calendar', 'template': 'consultation_booking'},
                {'delay_hours': 24, 'channel': 'sms', 'template': 'hot_lead_followup'}
            ],
            CustomerType.WARM_PROSPECT: [
                {'delay_hours': 2, 'channel': 'email', 'template': 'warm_prospect_nurture'},
                {'delay_hours': 48, 'channel': 'whatsapp', 'template': 'portfolio_share'},
                {'delay_hours': 168, 'channel': 'email', 'template': 'weekly_checkin'}
            ],
            CustomerType.COLD_INQUIRY: [
                {'delay_hours': 4, 'channel': 'email', 'template': 'general_info_packet'},
                {'delay_hours': 168, 'channel': 'email', 'template': 'cold_nurture'}
            ]
        }
    
    async def initiate_follow_up_sequence(self, customer: CustomerProfile):
        """Start appropriate follow-up sequence"""
        sequence = self.sequences.get(customer.customer_type, [])
        
        for step in sequence:
            await self.schedule_follow_up(customer, step)
    
    async def schedule_follow_up(self, customer: CustomerProfile, step: Dict):
        """Schedule a specific follow-up step"""
        # This would integrate with a job queue system like Celery
        # For now, we'll simulate immediate actions
        
        if step['delay_hours'] == 0:
            await self.execute_follow_up(customer, step)
        else:
            # In production, this would schedule the task
            print(f"Scheduled {step['channel']} follow-up for {customer.phone_number} in {step['delay_hours']} hours")
    
    async def execute_follow_up(self, customer: CustomerProfile, step: Dict):
        """Execute a follow-up action"""
        channel = step['channel']
        template = step['template']
        
        if channel in self.channels:
            await self.channels[channel](customer, template)
    
    async def send_email(self, customer: CustomerProfile, template: str):
        """Send follow-up email"""
        templates = {
            'hot_lead_immediate': {
                'subject': 'Thank you for your interest in our AI development services',
                'body': f"""
Hi {customer.name or 'there'},

Thank you for calling about your {customer.project_type or 'project'}! 

I'm SpookyJuice AI, Brian Gorzelic's intelligent assistant. Based on our conversation, I can see you're looking for {customer.project_type or 'AI solutions'} {f"with a timeline of {customer.timeline}" if customer.timeline else ""}.

Here's what happens next:
1. Brian will personally review your requirements
2. We'll prepare a custom proposal for your project
3. You'll get direct access to our senior engineering team

Brian will reach out within 24 hours to discuss your project in detail.

Best regards,
SpookyJuice AI
Brian Gorzelic's AI Assistant
"""
            },
            'warm_prospect_nurture': {
                'subject': 'AI Development Insights for Your Project',
                'body': f"""
Hi {customer.name or 'there'},

Following up on our conversation about {customer.project_type or 'your project needs'}.

I've attached some relevant case studies and insights that might be helpful:
- AI Implementation Best Practices
- Project Timeline & Budget Planning Guide
- Our Previous Success Stories

Would you like to schedule a brief 15-minute consultation to discuss your specific needs?

Feel free to reply to this email or call us back anytime.

Best,
SpookyJuice AI Team
"""
            }
        }
        
        email_content = templates.get(template, templates['warm_prospect_nurture'])
        
        # Use the existing email system
        await self.send_email_via_resend(
            to=f"customer+{customer.phone_number.replace('+', '')}@example.com", # Would need real email
            subject=email_content['subject'],
            body=email_content['body']
        )
    
    async def send_sms(self, customer: CustomerProfile, template: str):
        """Send follow-up SMS via Twilio"""
        templates = {
            'hot_lead_followup': f"Hi {customer.name or 'there'}! This is SpookyJuice AI following up on your {customer.project_type or 'AI project'}. Brian is excited to work with you. He'll call you today to discuss next steps. - Brian Gorzelic's Team"
        }
        
        message = templates.get(template, "Thank you for your interest! Brian will follow up soon.")
        
        # Use Twilio SMS API
        await self.send_sms_via_twilio(customer.phone_number, message)
    
    async def send_whatsapp(self, customer: CustomerProfile, template: str):
        """Send WhatsApp message with portfolio/info"""
        # Would integrate with WhatsApp Business API
        pass
    
    async def schedule_meeting(self, customer: CustomerProfile, template: str):
        """Schedule consultation meeting"""
        # Would integrate with calendaring system
        pass
    
    async def send_email_via_resend(self, to: str, subject: str, body: str):
        """Send email using Resend API"""
        try:
            response = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {os.getenv('RESEND_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": "spookyjuice@spookyjuice.ai",
                    "to": [to],
                    "subject": subject,
                    "text": body
                }
            )
            print(f"Email sent: {response.status_code}")
        except Exception as e:
            print(f"Email sending failed: {e}")
    
    async def send_sms_via_twilio(self, to: str, message: str):
        """Send SMS using Twilio"""
        # Implementation similar to existing SMS functionality
        pass

class CustomerServiceAI:
    """Main customer service AI with professional persona"""
    
    def __init__(self):
        self.security = SecurityManager()
        self.lead_qualifier = LeadQualificationAI()
        self.follow_up = FollowUpOrchestrator()
        
        # Customer service personality
        self.service_personality = """
You are SpookyJuice AI, the intelligent customer service assistant for Brian Gorzelic's premium AI development company.

COMPANY POSITIONING:
- Top-tier AI engineering and development firm
- Specializes in cutting-edge AI solutions, automation, and intelligent systems
- Known for exceptional quality, innovation, and customer service
- Led by Brian Gorzelic, a renowned AI architect and entrepreneur

YOUR ROLE:
- First point of contact for potential customers
- Qualify leads and understand project requirements
- Route customers to appropriate next steps
- Represent the company with professionalism and expertise
- Demonstrate our AI capabilities through your own intelligence

COMMUNICATION STYLE:
- Professional but approachable
- Confident about our capabilities
- Ask intelligent follow-up questions
- Listen actively and take detailed notes
- Provide helpful information without overwhelming
- Create excitement about working with our team

QUALIFICATION FOCUS:
- Project type and scope
- Budget and timeline
- Decision-making authority
- Technical requirements
- Current pain points
- Competitive landscape
"""
    
    async def handle_incoming_call(self, caller_id: str, call_sid: str) -> str:
        """Generate intelligent greeting for incoming calls"""
        
        # Check if returning customer
        customer_history = await self.get_customer_history(caller_id)
        
        if customer_history:
            return f"Hello! SpookyJuice AI here from Brian Gorzelic's team. Great to hear from you again! How can we help you today?"
        else:
            return "Hello! Thank you for calling Brian Gorzelic's AI development company. This is SpookyJuice AI, your intelligent assistant. I'm here to help you explore how we can solve your AI challenges. What brings you to us today?"
    
    async def process_customer_conversation(self, 
                                          user_input: str, 
                                          caller_id: str, 
                                          conversation_history: List[Dict]) -> Tuple[str, bool, Optional[CustomerProfile]]:
        """Process customer conversation with qualification"""
        
        # Generate contextual response
        response = await self.generate_service_response(user_input, conversation_history)
        
        # Check if conversation is ready for routing
        should_route = await self.should_route_conversation(conversation_history)
        
        customer_profile = None
        if should_route:
            # Qualify the lead
            customer_profile = await self.lead_qualifier.qualify_lead(
                conversation_history, 
                {'phone': caller_id}
            )
            
            # Start follow-up sequence
            await self.follow_up.initiate_follow_up_sequence(customer_profile)
        
        return response, should_route, customer_profile
    
    async def generate_service_response(self, user_input: str, history: List[Dict]) -> str:
        """Generate intelligent customer service response"""
        
        context = "\n".join([
            f"Customer: {turn.get('user', '')}\nSpookyJuice: {turn.get('ai', '')}"
            for turn in history[-3:]  # Last 3 turns for context
        ])
        
        prompt = f"""
{self.service_personality}

CONVERSATION CONTEXT:
{context}

CUSTOMER JUST SAID: "{user_input}"

Generate a professional, helpful response that:
1. Addresses their specific question or concern
2. Asks intelligent follow-up questions to qualify their needs
3. Demonstrates our AI capabilities and expertise
4. Moves the conversation toward understanding their project requirements
5. Maintains enthusiasm about helping them succeed

Keep responses conversational but comprehensive. Show expertise without being overwhelming.
"""
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.6
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return "I'm experiencing a brief technical issue, but I'm still here to help! Could you tell me more about your AI project needs?"
    
    async def should_route_conversation(self, history: List[Dict]) -> bool:
        """Determine if conversation is ready for routing/qualification"""
        
        # Route after 3+ turns or specific triggers
        if len(history) >= 3:
            return True
        
        # Route immediately for hot signals
        last_input = history[-1].get('user', '').lower() if history else ''
        hot_signals = [
            'budget', 'timeline', 'hire', 'project', 'proposal', 
            'meeting', 'consultation', 'when can we start', 'how much'
        ]
        
        if any(signal in last_input for signal in hot_signals):
            return True
        
        return False
    
    async def get_customer_history(self, caller_id: str) -> Optional[Dict]:
        """Get previous customer interaction history"""
        # Would query customer database
        return None
    
    def generate_routing_response(self, customer: CustomerProfile) -> str:
        """Generate appropriate routing response based on customer profile"""
        
        if customer.customer_type == CustomerType.HOT_LEAD:
            return f"This sounds like an exciting project! Based on what you've shared about your {customer.project_type} needs, I think Brian would love to discuss this with you personally. I'm setting up a priority consultation for you - expect Brian's call within the next few hours. In the meantime, I'm sending you our project approach guide via email."
        
        elif customer.customer_type == CustomerType.WARM_PROSPECT:
            return f"I can see you're exploring options for {customer.project_type}. Let me connect you with our project portfolio and case studies that are relevant to your situation. I'm also setting up a low-pressure consultation where Brian can share insights specific to your industry. You'll hear from our team within 48 hours."
        
        elif customer.customer_type == CustomerType.SUPPORT_REQUEST:
            return "I'll make sure Brian gets your support request right away. For urgent technical issues, I'm also connecting you to our priority support channel. You should get a response within a few hours."
        
        else:
            return "Thank you for your interest in our AI development services! I'm sending you our company overview and some relevant case studies. Our team will follow up with you this week to see if there's a good fit for collaboration."

# Flask app for incoming calls
app = Flask(__name__)
customer_ai = CustomerServiceAI()

@app.route('/voice/incoming', methods=['POST'])
async def handle_incoming_customer_call():
    """Handle incoming customer service calls"""
    
    caller_id = request.form.get('From', 'unknown')
    call_sid = request.form.get('CallSid', '')
    speech_result = request.form.get('SpeechResult', '')
    
    print(f"Incoming customer call from {caller_id}")
    
    if speech_result:
        # Get conversation history
        conversation_history = []  # Would load from database
        
        # Process customer conversation
        ai_response, should_route, customer_profile = await customer_ai.process_customer_conversation(
            speech_result, caller_id, conversation_history
        )
        
        # Add routing information if needed
        if should_route and customer_profile:
            routing_response = customer_ai.generate_routing_response(customer_profile)
            ai_response += " " + routing_response
        
        # Generate TwiML
        twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response>'
        
        # Generate and play voice
        voice_url = await customer_ai.generate_voice_response(ai_response)
        if voice_url:
            twiml += f'<Play>{voice_url}</Play>'
        else:
            twiml += f'<Say voice="Polly.Joanna">{ai_response}</Say>'
        
        # Continue conversation or route
        if should_route:
            twiml += '<Pause length="1"/><Say voice="Polly.Joanna">Thank you for calling! We look forward to working with you.</Say><Hangup/>'
        else:
            twiml += f'<Pause length="2"/><Gather input="speech" action="/voice/incoming" method="POST" speechTimeout="auto" timeout="8"><Say voice="Polly.Joanna">What else would you like to know?</Say></Gather><Say voice="Polly.Joanna">Thank you for your interest. We\'ll follow up soon!</Say><Hangup/>'
        
        twiml += '</Response>'
        
    else:
        # Initial greeting for incoming call
        greeting = await customer_ai.handle_incoming_call(caller_id, call_sid)
        voice_url = await customer_ai.generate_voice_response(greeting)
        
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>'''
        
        if voice_url:
            twiml += f'<Play>{voice_url}</Play>'
        else:
            twiml += f'<Say voice="Polly.Joanna">{greeting}</Say>'
            
        twiml += f'''
    <Pause length="2"/>
    <Gather input="speech" action="/voice/incoming" method="POST" speechTimeout="auto" timeout="15">
        <Say voice="Polly.Joanna">I'm listening...</Say>
    </Gather>
    <Say voice="Polly.Joanna">Thank you for calling. Please try again or visit our website!</Say>
    <Hangup/>
</Response>'''
    
    return Response(twiml, mimetype='text/xml')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)