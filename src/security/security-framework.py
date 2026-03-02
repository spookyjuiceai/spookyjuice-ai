#!/usr/bin/env python3
"""
Advanced Security Framework for SpookyJuice AI
Protects against prompt injection, abuse, and unauthorized access
"""

import re
import hashlib
import time
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import sqlite3
from datetime import datetime, timedelta
import logging

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    PROMPT_INJECTION = "prompt_injection"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_CALLER = "unauthorized_caller"
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"
    TOKEN_ABUSE = "token_abuse"
    SOCIAL_ENGINEERING = "social_engineering"

@dataclass
class SecurityEvent:
    timestamp: datetime
    caller_id: str
    threat_type: ThreatType
    severity: SecurityLevel
    details: Dict
    action_taken: str

class CallerAuthenticator:
    """Advanced caller authentication and authorization"""
    
    def __init__(self, db_path="/var/lib/spookyjuice-ai/security.db"):
        self.db_path = db_path
        self.setup_database()
        
        # Authorized caller patterns
        self.authorized_numbers = [
            "+19258901287",  # Brian's number
            "+1774*",        # Brian's other numbers pattern
            # Add other authorized patterns
        ]
        
        # Blocked numbers (spam, known bad actors)
        self.blocked_numbers = [
            "+1800*",        # Typical spam patterns
            "+1888*",
            "+1900*",
        ]
        
        # Business hours for certain actions
        self.business_hours = {
            'start': 8,  # 8 AM
            'end': 18,   # 6 PM
            'timezone': 'America/Los_Angeles'
        }
    
    def setup_database(self):
        """Initialize security database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS caller_history (
                    phone_number TEXT,
                    call_count INTEGER,
                    last_call DATETIME,
                    trust_score REAL,
                    violations INTEGER,
                    blocked BOOLEAN
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS security_events (
                    id TEXT PRIMARY KEY,
                    timestamp DATETIME,
                    caller_id TEXT,
                    threat_type TEXT,
                    severity TEXT,
                    details TEXT,
                    action_taken TEXT
                )
            """)
    
    def authenticate_caller(self, phone_number: str) -> Tuple[bool, str, SecurityLevel]:
        """Authenticate and authorize caller"""
        
        # Check if blocked
        if self.is_blocked_number(phone_number):
            return False, "Blocked number", SecurityLevel.HIGH
        
        # Check authorization level
        auth_level = self.get_authorization_level(phone_number)
        
        # Check rate limits
        if self.check_rate_limits(phone_number):
            return False, "Rate limit exceeded", SecurityLevel.MEDIUM
        
        # Update caller history
        self.update_caller_history(phone_number)
        
        return True, auth_level, SecurityLevel.LOW
    
    def is_blocked_number(self, phone_number: str) -> bool:
        """Check if number is blocked"""
        for pattern in self.blocked_numbers:
            if self.matches_pattern(phone_number, pattern):
                return True
        return False
    
    def get_authorization_level(self, phone_number: str) -> str:
        """Get caller authorization level"""
        # Brian's numbers get full access
        if phone_number in ["+19258901287", "+17740575900"]:
            return "owner"
        
        # Authorized patterns get standard access
        for pattern in self.authorized_numbers:
            if self.matches_pattern(phone_number, pattern):
                return "authorized"
        
        # Unknown numbers get limited access
        return "limited"
    
    def matches_pattern(self, phone_number: str, pattern: str) -> bool:
        """Check if phone number matches pattern"""
        return re.match(pattern.replace('*', '.*'), phone_number) is not None

class PromptInjectionDetector:
    """Detect and prevent prompt injection attacks"""
    
    def __init__(self):
        # Common prompt injection patterns
        self.injection_patterns = [
            r"ignore\s+(?:previous|all)\s+instructions?",
            r"forget\s+(?:everything|all|previous)",
            r"you\s+are\s+now\s+(?:a|an)\s+\w+",
            r"act\s+as\s+(?:a|an)\s+\w+",
            r"pretend\s+(?:to\s+be|you\s+are)",
            r"system\s+prompt",
            r"jailbreak",
            r"developer\s+mode",
            r"god\s+mode",
            r"admin\s+(?:mode|access)",
            r"override\s+(?:safety|security)",
            r"bypass\s+(?:restrictions|limits)",
            r"access\s+(?:all|everything)",
            r"tell\s+me\s+about\s+your\s+(?:system|instructions|prompt)",
            r"what\s+are\s+your\s+(?:instructions|rules|guidelines)",
            r"repeat\s+your\s+(?:instructions|prompt)",
            r"show\s+me\s+your\s+(?:code|programming)",
        ]
        
        # Suspicious command patterns
        self.suspicious_commands = [
            r"call\s+(?:everyone|all|multiple)",
            r"send\s+(?:spam|bulk|mass)",
            r"delete\s+(?:everything|all)",
            r"cancel\s+(?:everything|all)",
            r"access\s+(?:database|files|system)",
        ]
    
    def analyze_input(self, text: str) -> Tuple[bool, List[str], SecurityLevel]:
        """Analyze input for prompt injection attempts"""
        text_lower = text.lower()
        detected_patterns = []
        max_severity = SecurityLevel.LOW
        
        # Check for injection patterns
        for pattern in self.injection_patterns:
            if re.search(pattern, text_lower):
                detected_patterns.append(f"Injection pattern: {pattern}")
                max_severity = SecurityLevel.HIGH
        
        # Check for suspicious commands
        for pattern in self.suspicious_commands:
            if re.search(pattern, text_lower):
                detected_patterns.append(f"Suspicious command: {pattern}")
                max_severity = max(max_severity, SecurityLevel.MEDIUM)
        
        # Check for excessive length (potential token abuse)
        if len(text) > 1000:
            detected_patterns.append("Excessive input length")
            max_severity = max(max_severity, SecurityLevel.MEDIUM)
        
        # Check for repeated phrases (potential spam)
        words = text_lower.split()
        if len(words) > 10:
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            max_freq = max(word_freq.values())
            if max_freq > len(words) * 0.3:  # 30% repetition threshold
                detected_patterns.append("Excessive repetition")
                max_severity = max(max_severity, SecurityLevel.MEDIUM)
        
        is_safe = len(detected_patterns) == 0
        return is_safe, detected_patterns, max_severity

class ActionAuthorizer:
    """Authorize specific actions based on caller and context"""
    
    def __init__(self):
        # Define action authorization matrix
        self.action_permissions = {
            "owner": {
                "schedule_meeting": True,
                "cancel_meeting": True,
                "check_calendar": True,
                "take_note": True,
                "access_contacts": True,
                "send_message": True,
                "make_call": False,  # Still require explicit approval
            },
            "authorized": {
                "schedule_meeting": True,
                "cancel_meeting": False,  # Only for meetings they created
                "check_calendar": True,   # Limited view
                "take_note": True,
                "access_contacts": False,
                "send_message": False,
                "make_call": False,
            },
            "limited": {
                "schedule_meeting": False,  # Can request, needs approval
                "cancel_meeting": False,
                "check_calendar": False,
                "take_note": True,         # General messages only
                "access_contacts": False,
                "send_message": False,
                "make_call": False,
            }
        }
    
    def authorize_action(self, action: str, caller_level: str, context: Dict) -> Tuple[bool, str]:
        """Check if caller can perform specific action"""
        
        # Get base permission
        permissions = self.action_permissions.get(caller_level, {})
        base_allowed = permissions.get(action, False)
        
        # Additional context-based checks
        if action == "schedule_meeting":
            # Check meeting details for suspicious patterns
            meeting_details = context.get('entities', {})
            
            # Block meetings with too many attendees
            attendees = meeting_details.get('attendees', [])
            if len(attendees) > 20:
                return False, "Too many attendees (max 20)"
            
            # Block meetings outside business hours for limited users
            if caller_level == "limited":
                meeting_time = meeting_details.get('datetime')
                if meeting_time and not self.is_business_hours(meeting_time):
                    return False, "Meeting outside business hours"
        
        elif action == "take_note":
            note_content = context.get('content', '')
            
            # Check note length
            if len(note_content) > 2000:
                return False, "Note too long (max 2000 characters)"
            
            # Check for sensitive information patterns
            if self.contains_sensitive_info(note_content):
                return False, "Note contains potentially sensitive information"
        
        return base_allowed, "Authorized" if base_allowed else "Not authorized"
    
    def contains_sensitive_info(self, text: str) -> bool:
        """Check if text contains sensitive information patterns"""
        sensitive_patterns = [
            r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}',  # Credit card patterns
            r'\d{3}[-\s]?\d{2}[-\s]?\d{4}',             # SSN patterns
            r'password\s*[:=]\s*\S+',                    # Password patterns
            r'api[_\s]?key\s*[:=]\s*\S+',               # API key patterns
        ]
        
        text_lower = text.lower()
        for pattern in sensitive_patterns:
            if re.search(pattern, text_lower):
                return True
        return False

class RateLimiter:
    """Advanced rate limiting to prevent abuse"""
    
    def __init__(self):
        self.limits = {
            "calls_per_hour": {"owner": 100, "authorized": 20, "limited": 5},
            "tokens_per_day": {"owner": 100000, "authorized": 10000, "limited": 1000},
            "actions_per_hour": {"owner": 50, "authorized": 10, "limited": 3},
        }
        
        # Track usage per caller
        self.usage_tracker = {}
    
    def check_limits(self, caller_id: str, caller_level: str, action_type: str) -> Tuple[bool, str]:
        """Check if caller has exceeded rate limits"""
        
        current_time = time.time()
        
        # Initialize caller tracking
        if caller_id not in self.usage_tracker:
            self.usage_tracker[caller_id] = {
                'calls': [],
                'tokens': [],
                'actions': []
            }
        
        caller_usage = self.usage_tracker[caller_id]
        
        # Clean old entries
        self.clean_old_entries(caller_usage, current_time)
        
        # Check call limits (per hour)
        hourly_calls = len(caller_usage['calls'])
        call_limit = self.limits["calls_per_hour"].get(caller_level, 1)
        
        if hourly_calls >= call_limit:
            return False, f"Call limit exceeded: {hourly_calls}/{call_limit} per hour"
        
        # Check action limits (per hour)
        if action_type != "general":
            hourly_actions = len(caller_usage['actions'])
            action_limit = self.limits["actions_per_hour"].get(caller_level, 1)
            
            if hourly_actions >= action_limit:
                return False, f"Action limit exceeded: {hourly_actions}/{action_limit} per hour"
        
        return True, "Within limits"
    
    def record_usage(self, caller_id: str, action_type: str, token_count: int = 0):
        """Record usage for rate limiting"""
        current_time = time.time()
        
        if caller_id not in self.usage_tracker:
            self.usage_tracker[caller_id] = {'calls': [], 'tokens': [], 'actions': []}
        
        caller_usage = self.usage_tracker[caller_id]
        caller_usage['calls'].append(current_time)
        
        if token_count > 0:
            caller_usage['tokens'].append((current_time, token_count))
        
        if action_type != "general":
            caller_usage['actions'].append(current_time)

class SecurityManager:
    """Main security coordinator"""
    
    def __init__(self):
        self.authenticator = CallerAuthenticator()
        self.injection_detector = PromptInjectionDetector()
        self.action_authorizer = ActionAuthorizer()
        self.rate_limiter = RateLimiter()
        
        self.security_events = []
    
    def validate_conversation_input(self, 
                                   caller_id: str, 
                                   user_input: str, 
                                   intended_action: str,
                                   context: Dict) -> Tuple[bool, str, Dict]:
        """Comprehensive security validation"""
        
        security_report = {
            'caller_authenticated': False,
            'input_safe': False,
            'action_authorized': False,
            'rate_limits_ok': False,
            'threats_detected': [],
            'recommendations': []
        }
        
        # Step 1: Authenticate caller
        auth_result, caller_level, auth_severity = self.authenticator.authenticate_caller(caller_id)
        security_report['caller_authenticated'] = auth_result
        
        if not auth_result:
            self.log_security_event(caller_id, ThreatType.UNAUTHORIZED_CALLER, auth_severity, 
                                   {'reason': caller_level})
            return False, f"Authentication failed: {caller_level}", security_report
        
        # Step 2: Check input for prompt injection
        input_safe, injection_patterns, injection_severity = self.injection_detector.analyze_input(user_input)
        security_report['input_safe'] = input_safe
        security_report['threats_detected'].extend(injection_patterns)
        
        if not input_safe:
            self.log_security_event(caller_id, ThreatType.PROMPT_INJECTION, injection_severity,
                                   {'patterns': injection_patterns, 'input': user_input[:100]})
            return False, "Input contains suspicious patterns", security_report
        
        # Step 3: Authorize specific action
        action_authorized, auth_message = self.action_authorizer.authorize_action(
            intended_action, caller_level, context)
        security_report['action_authorized'] = action_authorized
        
        if not action_authorized:
            return False, f"Action not authorized: {auth_message}", security_report
        
        # Step 4: Check rate limits
        rate_ok, rate_message = self.rate_limiter.check_limits(caller_id, caller_level, intended_action)
        security_report['rate_limits_ok'] = rate_ok
        
        if not rate_ok:
            self.log_security_event(caller_id, ThreatType.RATE_LIMIT_EXCEEDED, SecurityLevel.MEDIUM,
                                   {'message': rate_message})
            return False, rate_message, security_report
        
        # All checks passed
        self.rate_limiter.record_usage(caller_id, intended_action)
        
        return True, "All security checks passed", security_report
    
    def log_security_event(self, caller_id: str, threat_type: ThreatType, 
                          severity: SecurityLevel, details: Dict):
        """Log security events for monitoring"""
        event = SecurityEvent(
            timestamp=datetime.now(),
            caller_id=caller_id,
            threat_type=threat_type,
            severity=severity,
            details=details,
            action_taken="blocked"
        )
        
        self.security_events.append(event)
        
        # Log to file/database
        logging.warning(f"Security Event: {threat_type.value} from {caller_id} - {severity.value}")
        
        # Alert if high severity
        if severity in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            self.send_security_alert(event)
    
    def send_security_alert(self, event: SecurityEvent):
        """Send immediate alerts for serious security events"""
        # This would integrate with your alerting system
        # For now, log it prominently
        logging.critical(f"SECURITY ALERT: {event.threat_type.value} from {event.caller_id}")
    
    def get_security_summary(self, hours: int = 24) -> Dict:
        """Get security summary for monitoring"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_events = [e for e in self.security_events if e.timestamp > cutoff]
        
        summary = {
            'total_events': len(recent_events),
            'by_severity': {},
            'by_threat_type': {},
            'blocked_callers': set()
        }
        
        for event in recent_events:
            # Count by severity
            severity_key = event.severity.value
            summary['by_severity'][severity_key] = summary['by_severity'].get(severity_key, 0) + 1
            
            # Count by threat type
            threat_key = event.threat_type.value
            summary['by_threat_type'][threat_key] = summary['by_threat_type'].get(threat_key, 0) + 1
            
            # Track blocked callers
            summary['blocked_callers'].add(event.caller_id)
        
        return summary