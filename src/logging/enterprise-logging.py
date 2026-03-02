#!/usr/bin/env python3
"""
Enterprise-Grade Logging and Debugging System for SpookyJuice AI
Comprehensive logging, debugging, health checks, and monitoring
"""

import os
import json
import time
import logging
import traceback
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from pathlib import Path

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ComponentType(Enum):
    VOICE_ENGINE = "voice_engine"
    CONVERSATION_AI = "conversation_ai"  
    SECURITY_SYSTEM = "security_system"
    TASK_EXECUTOR = "task_executor"
    API_INTEGRATION = "api_integration"
    WEBHOOK_HANDLER = "webhook_handler"

@dataclass
class LogEntry:
    timestamp: datetime
    level: LogLevel
    component: ComponentType
    message: str
    details: Dict[str, Any]
    request_id: str
    caller_id: str
    call_sid: str
    execution_time_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float

class EnterpriseLogger:
    """Production-grade logging system with debugging capabilities"""
    
    def __init__(self, log_dir="/var/log/spookyjuice-ai"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup structured logging
        self.setup_logging()
        
        # Database for queryable logs
        self.db_path = self.log_dir / "logs.db"
        self.setup_database()
        
        # Performance tracking
        self.performance_metrics = {}
        
    def setup_logging(self):
        """Configure comprehensive logging"""
        
        # Create multiple log files
        log_format = '%(asctime)s | %(levelname)8s | %(name)20s | %(message)s'
        
        # Main application log
        main_handler = logging.FileHandler(self.log_dir / "spookyjuice-ai.log")
        main_handler.setFormatter(logging.Formatter(log_format))
        
        # Error-only log
        error_handler = logging.FileHandler(self.log_dir / "errors.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(log_format))
        
        # Security events log
        security_handler = logging.FileHandler(self.log_dir / "security.log")
        security_handler.setFormatter(logging.Formatter(log_format))
        
        # Performance log
        perf_handler = logging.FileHandler(self.log_dir / "performance.log") 
        perf_handler.setFormatter(logging.Formatter(log_format))
        
        # Console output
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
        ))
        
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            handlers=[main_handler, error_handler, console_handler],
            format=log_format
        )
        
        # Create specialized loggers
        self.main_logger = logging.getLogger('spookyjuice.main')
        self.voice_logger = logging.getLogger('spookyjuice.voice')
        self.ai_logger = logging.getLogger('spookyjuice.ai')
        self.security_logger = logging.getLogger('spookyjuice.security')
        self.api_logger = logging.getLogger('spookyjuice.api')
        
        # Add security handler to security logger
        self.security_logger.addHandler(security_handler)
        
    def setup_database(self):
        """Setup database for structured log queries"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS log_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    level TEXT,
                    component TEXT,
                    message TEXT,
                    details TEXT,
                    request_id TEXT,
                    caller_id TEXT,
                    call_sid TEXT,
                    execution_time_ms REAL,
                    memory_usage_mb REAL,
                    cpu_usage_percent REAL
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON log_entries(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_level ON log_entries(level)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_component ON log_entries(component)
            """)
    
    def log_event(self, 
                  level: LogLevel,
                  component: ComponentType, 
                  message: str,
                  details: Optional[Dict] = None,
                  request_id: str = "",
                  caller_id: str = "",
                  call_sid: str = "",
                  execution_time_ms: float = 0.0):
        """Log event with comprehensive context"""
        
        # Get system metrics
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent()
        
        # Create log entry
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            component=component,
            message=message,
            details=details or {},
            request_id=request_id,
            caller_id=caller_id,
            call_sid=call_sid,
            execution_time_ms=execution_time_ms,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage
        )
        
        # Log to file
        logger = getattr(self, f"{component.value.split('_')[0]}_logger", self.main_logger)
        log_msg = f"{message} | Request: {request_id} | Caller: {caller_id} | Time: {execution_time_ms}ms"
        
        if level == LogLevel.DEBUG:
            logger.debug(log_msg)
        elif level == LogLevel.INFO:
            logger.info(log_msg)
        elif level == LogLevel.WARNING:
            logger.warning(log_msg)
        elif level == LogLevel.ERROR:
            logger.error(log_msg)
        elif level == LogLevel.CRITICAL:
            logger.critical(log_msg)
        
        # Store in database
        self.store_log_entry(entry)
        
        # Real-time monitoring alerts
        if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            self.trigger_alert(entry)
    
    def store_log_entry(self, entry: LogEntry):
        """Store log entry in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO log_entries 
                    (timestamp, level, component, message, details, request_id, caller_id, call_sid, execution_time_ms, memory_usage_mb, cpu_usage_percent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.timestamp,
                    entry.level.value,
                    entry.component.value,
                    entry.message,
                    json.dumps(entry.details),
                    entry.request_id,
                    entry.caller_id, 
                    entry.call_sid,
                    entry.execution_time_ms,
                    entry.memory_usage_mb,
                    entry.cpu_usage_percent
                ))
        except Exception as e:
            # Fallback logging if database fails
            self.main_logger.error(f"Failed to store log entry: {e}")
    
    def trigger_alert(self, entry: LogEntry):
        """Trigger alerts for critical issues"""
        alert_message = f"🚨 ALERT: {entry.level.value} in {entry.component.value}\n{entry.message}"
        
        # Log the alert
        self.main_logger.critical(alert_message)
        
        # In production, this would send notifications
        # via email, Slack, PagerDuty, etc.
        
    def get_logs(self, 
                 hours: int = 24,
                 level: Optional[LogLevel] = None,
                 component: Optional[ComponentType] = None,
                 caller_id: Optional[str] = None) -> List[Dict]:
        """Query logs with filters"""
        
        cutoff = datetime.now() - timedelta(hours=hours)
        
        query = "SELECT * FROM log_entries WHERE timestamp > ?"
        params = [cutoff]
        
        if level:
            query += " AND level = ?"
            params.append(level.value)
            
        if component:
            query += " AND component = ?"
            params.append(component.value)
            
        if caller_id:
            query += " AND caller_id = ?"
            params.append(caller_id)
        
        query += " ORDER BY timestamp DESC LIMIT 1000"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_system_health(self) -> Dict:
        """Get comprehensive system health report"""
        
        # System metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Process metrics
        process = psutil.Process()
        
        # Error rates (last hour)
        recent_logs = self.get_logs(hours=1)
        total_events = len(recent_logs)
        error_events = len([log for log in recent_logs if log['level'] in ['ERROR', 'CRITICAL']])
        error_rate = (error_events / total_events * 100) if total_events > 0 else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'memory_usage_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_usage_percent': disk.used / disk.total * 100,
                'disk_free_gb': disk.free / (1024**3),
                'cpu_usage_percent': psutil.cpu_percent(),
                'uptime_hours': time.time() - psutil.boot_time() / 3600
            },
            'process': {
                'memory_usage_mb': process.memory_info().rss / (1024**2),
                'cpu_percent': process.cpu_percent(),
                'num_threads': process.num_threads(),
                'status': process.status()
            },
            'application': {
                'total_events_hour': total_events,
                'error_events_hour': error_events,
                'error_rate_percent': round(error_rate, 2),
                'last_error': recent_logs[0] if error_events > 0 else None
            }
        }

class DebugManager:
    """Advanced debugging and troubleshooting system"""
    
    def __init__(self, logger: EnterpriseLogger):
        self.logger = logger
        
    def debug_webhook_connectivity(self, webhook_url: str) -> Dict:
        """Debug webhook connectivity issues"""
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'webhook_url': webhook_url,
            'tests': {}
        }
        
        # Test 1: Basic HTTP connectivity
        try:
            response = requests.get(webhook_url, timeout=10)
            results['tests']['http_connectivity'] = {
                'status': 'success',
                'response_code': response.status_code,
                'response_time_ms': response.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            results['tests']['http_connectivity'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        # Test 2: SSL certificate validation
        try:
            response = requests.get(webhook_url, timeout=5, verify=True)
            results['tests']['ssl_validation'] = {'status': 'success'}
        except Exception as e:
            results['tests']['ssl_validation'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        # Test 3: Twilio webhook simulation
        try:
            test_data = {
                'From': '+15551234567',
                'To': '+14155981480',
                'CallSid': 'test-debug-call',
                'AccountSid': 'test-account'
            }
            response = requests.post(webhook_url, data=test_data, timeout=10)
            results['tests']['webhook_functionality'] = {
                'status': 'success' if response.status_code == 200 else 'failed',
                'response_code': response.status_code,
                'response_body': response.text[:500]
            }
        except Exception as e:
            results['tests']['webhook_functionality'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        return results
    
    def debug_voice_generation(self, voice_id: str, test_text: str) -> Dict:
        """Debug ElevenLabs voice generation"""
        
        start_time = time.time()
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'voice_id': voice_id,
            'test_text': test_text,
            'tests': {}
        }
        
        # Test API connectivity
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
            headers = {
                "Accept": "audio/mpeg",
                "xi-api-key": os.getenv('ELEVENLABS_API_KEY'),
                "Content-Type": "application/json"
            }
            data = {
                "text": test_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.15,
                    "similarity_boost": 0.98,
                    "style": 0.45,
                    "use_speaker_boost": True
                }
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=15)
            generation_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                results['tests']['voice_generation'] = {
                    'status': 'success',
                    'generation_time_ms': generation_time,
                    'audio_size_bytes': len(response.content),
                    'rate_limit_remaining': response.headers.get('X-RateLimit-Remaining', 'unknown')
                }
            else:
                results['tests']['voice_generation'] = {
                    'status': 'failed',
                    'response_code': response.status_code,
                    'error_body': response.text
                }
                
        except Exception as e:
            results['tests']['voice_generation'] = {
                'status': 'failed',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
        
        return results
    
    def debug_ai_processing(self, test_prompt: str) -> Dict:
        """Debug OpenAI API connectivity and processing"""
        
        start_time = time.time()
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'test_prompt': test_prompt,
            'tests': {}
        }
        
        try:
            import openai
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": test_prompt}],
                max_tokens=100
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            results['tests']['ai_processing'] = {
                'status': 'success',
                'processing_time_ms': processing_time,
                'tokens_used': response.usage.total_tokens,
                'response_preview': response.choices[0].message.content[:100]
            }
            
        except Exception as e:
            results['tests']['ai_processing'] = {
                'status': 'failed',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
        
        return results

class HealthCheckSystem:
    """Comprehensive health monitoring and alerting"""
    
    def __init__(self, logger: EnterpriseLogger):
        self.logger = logger
        
    def run_health_checks(self) -> Dict:
        """Run all system health checks"""
        
        checks = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'checks': {}
        }
        
        # Check 1: Service availability
        checks['checks']['service_availability'] = self.check_service_availability()
        
        # Check 2: Database connectivity
        checks['checks']['database_connectivity'] = self.check_database()
        
        # Check 3: External APIs
        checks['checks']['external_apis'] = self.check_external_apis()
        
        # Check 4: System resources
        checks['checks']['system_resources'] = self.check_system_resources()
        
        # Check 5: Webhook endpoints
        checks['checks']['webhook_endpoints'] = self.check_webhooks()
        
        # Determine overall status
        failed_checks = [k for k, v in checks['checks'].items() if v.get('status') != 'healthy']
        
        if len(failed_checks) == 0:
            checks['overall_status'] = 'healthy'
        elif len(failed_checks) <= 2:
            checks['overall_status'] = 'degraded'
        else:
            checks['overall_status'] = 'unhealthy'
        
        # Log health status
        self.logger.log_event(
            LogLevel.INFO if checks['overall_status'] == 'healthy' else LogLevel.WARNING,
            ComponentType.WEBHOOK_HANDLER,
            f"Health check complete: {checks['overall_status']}",
            details=checks
        )
        
        return checks
    
    def check_service_availability(self) -> Dict:
        """Check if core services are running"""
        try:
            # Check if SpookyJuice AI process is running
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'spookyjuice-ai' in ' '.join(proc.info['cmdline'] or []):
                    return {
                        'status': 'healthy',
                        'pid': proc.info['pid'],
                        'uptime_seconds': time.time() - proc.create_time()
                    }
            
            return {'status': 'unhealthy', 'error': 'SpookyJuice AI process not found'}
            
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    def check_external_apis(self) -> Dict:
        """Check external API connectivity"""
        apis = {
            'elevenlabs': 'https://api.elevenlabs.io/v1/user',
            'openai': 'https://api.openai.com/v1/models',
            'twilio': f'https://api.twilio.com/2010-04-01/Accounts/{os.getenv("TWILIO_ACCOUNT_SID")}.json'
        }
        
        results = {}
        
        for api_name, url in apis.items():
            try:
                headers = {}
                if api_name == 'elevenlabs':
                    headers['xi-api-key'] = os.getenv('ELEVENLABS_API_KEY')
                elif api_name == 'openai':
                    headers['Authorization'] = f"Bearer {os.getenv('OPENAI_API_KEY')}"
                elif api_name == 'twilio':
                    auth = (os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
                
                response = requests.get(url, headers=headers, auth=auth if api_name == 'twilio' else None, timeout=5)
                
                results[api_name] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'response_code': response.status_code,
                    'response_time_ms': response.elapsed.total_seconds() * 1000
                }
                
            except Exception as e:
                results[api_name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
        
        return results

class TestSuiteRunner:
    """Automated test suite for all functionality"""
    
    def __init__(self, logger: EnterpriseLogger):
        self.logger = logger
        
    def run_full_test_suite(self) -> Dict:
        """Run comprehensive automated tests"""
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'test_suite_version': '1.0',
            'tests': {}
        }
        
        # Voice system tests
        results['tests']['voice_system'] = self.test_voice_system()
        
        # AI conversation tests
        results['tests']['ai_conversation'] = self.test_ai_conversation()
        
        # Security system tests
        results['tests']['security_system'] = self.test_security_system()
        
        # Integration tests
        results['tests']['integrations'] = self.test_integrations()
        
        # Performance tests
        results['tests']['performance'] = self.test_performance()
        
        # Calculate overall score
        passed_tests = sum(1 for test in results['tests'].values() if test.get('status') == 'passed')
        total_tests = len(results['tests'])
        results['overall_score'] = f"{passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)"
        
        return results
    
    def test_voice_system(self) -> Dict:
        """Test voice generation system"""
        debug_manager = DebugManager(self.logger)
        
        voice_test = debug_manager.debug_voice_generation(
            'O91ChHz6qxVDOmtvlMKZ',
            'Testing SpookyJuice AI voice system functionality'
        )
        
        return {
            'status': 'passed' if voice_test['tests']['voice_generation']['status'] == 'success' else 'failed',
            'details': voice_test
        }
    
    def test_ai_conversation(self) -> Dict:
        """Test AI conversation processing"""
        debug_manager = DebugManager(self.logger)
        
        ai_test = debug_manager.debug_ai_processing(
            'Test SpookyJuice AI conversation capabilities with this prompt'
        )
        
        return {
            'status': 'passed' if ai_test['tests']['ai_processing']['status'] == 'success' else 'failed',
            'details': ai_test
        }

# Initialize enterprise logging
enterprise_logger = EnterpriseLogger()

def create_test_runner():
    """Create and run comprehensive tests"""
    
    enterprise_logger.log_event(
        LogLevel.INFO,
        ComponentType.WEBHOOK_HANDLER,
        "Starting comprehensive system tests",
        details={'test_version': '1.0', 'environment': 'production'}
    )
    
    # Run health checks
    health_check = HealthCheckSystem(enterprise_logger)
    health_results = health_check.run_health_checks()
    
    # Run test suite
    test_runner = TestSuiteRunner(enterprise_logger) 
    test_results = test_runner.run_full_test_suite()
    
    return {
        'health_check': health_results,
        'test_results': test_results
    }

if __name__ == "__main__":
    results = create_test_runner()
    print("🧪 COMPREHENSIVE TESTING COMPLETE")
    print(json.dumps(results, indent=2))