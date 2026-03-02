#!/usr/bin/env python3
"""
Cloudflare Configuration Script for SpookyJuice AI Webhooks
Fixes webhook blocking issues automatically
"""

import os
import json
import requests
from typing import Dict, List

class CloudflareFixer:
    """Automatically configure Cloudflare for SpookyJuice AI webhooks"""
    
    def __init__(self, api_token: str, zone_id: str):
        self.api_token = api_token
        self.zone_id = zone_id
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        # Twilio IP ranges that need access
        self.twilio_ips = [
            "34.203.250.0/23",
            "34.218.240.0/21", 
            "34.218.248.0/23",
            "54.172.60.0/23",
            "54.244.51.0/24",
            "3.80.16.0/23",
            "3.95.0.0/20",
            "18.205.93.0/27",
            "35.156.191.128/25"
        ]
    
    def verify_access(self) -> bool:
        """Verify API token has required permissions"""
        try:
            response = requests.get(
                f"{self.base_url}/zones/{self.zone_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                zone_data = response.json()['result']
                print(f"✅ Zone access verified: {zone_data['name']}")
                return True
            else:
                print(f"❌ Zone access failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ API verification failed: {e}")
            return False
    
    def create_twilio_ip_rules(self) -> Dict:
        """Create IP access rules for Twilio webhooks"""
        
        results = {
            'created_rules': [],
            'errors': []
        }
        
        for ip_range in self.twilio_ips:
            try:
                rule_data = {
                    "mode": "whitelist",
                    "configuration": {
                        "target": "ip_range",
                        "value": ip_range
                    },
                    "notes": f"SpookyJuice AI - Twilio webhook access for {ip_range}"
                }
                
                response = requests.post(
                    f"{self.base_url}/zones/{self.zone_id}/firewall/access_rules/rules",
                    headers=self.headers,
                    json=rule_data,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    rule_id = response.json()['result']['id']
                    results['created_rules'].append({
                        'ip_range': ip_range,
                        'rule_id': rule_id
                    })
                    print(f"✅ Created IP rule for {ip_range}")
                else:
                    error_msg = response.json().get('errors', [{'message': 'Unknown error'}])[0]['message']
                    results['errors'].append({
                        'ip_range': ip_range,
                        'error': error_msg
                    })
                    print(f"⚠️ IP rule for {ip_range}: {error_msg}")
                    
            except Exception as e:
                results['errors'].append({
                    'ip_range': ip_range,
                    'error': str(e)
                })
                print(f"❌ Failed to create rule for {ip_range}: {e}")
        
        return results
    
    def create_voice_webhook_rules(self) -> Dict:
        """Create page rules for voice webhook paths"""
        
        webhook_paths = [
            "spookyjuice.ai/voice/*",
            "spookyjuice.ai/health",
            "spookyjuice.ai/debug/*"
        ]
        
        results = {
            'created_rules': [],
            'errors': []
        }
        
        for path in webhook_paths:
            try:
                rule_data = {
                    "targets": [{"target": "url", "constraint": {"operator": "matches", "value": path}}],
                    "actions": [
                        {"id": "security_level", "value": "essentially_off"},
                        {"id": "browser_check", "value": "off"},
                        {"id": "challenge_ttl", "value": 1800}
                    ],
                    "priority": 1,
                    "status": "active"
                }
                
                response = requests.post(
                    f"{self.base_url}/zones/{self.zone_id}/pagerules",
                    headers=self.headers,
                    json=rule_data,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    rule_id = response.json()['result']['id']
                    results['created_rules'].append({
                        'path': path,
                        'rule_id': rule_id
                    })
                    print(f"✅ Created page rule for {path}")
                else:
                    error_msg = response.json().get('errors', [{'message': 'Unknown error'}])[0]['message']
                    results['errors'].append({
                        'path': path,
                        'error': error_msg
                    })
                    print(f"⚠️ Page rule for {path}: {error_msg}")
                    
            except Exception as e:
                results['errors'].append({
                    'path': path,
                    'error': str(e)
                })
                print(f"❌ Failed to create rule for {path}: {e}")
        
        return results
    
    def test_webhook_accessibility(self) -> Dict:
        """Test webhook accessibility after configuration"""
        
        webhooks = [
            "https://spookyjuice.ai/health",
            "https://spookyjuice.ai/voice/secure",
            "https://spookyjuice.ai/voice/incoming"
        ]
        
        results = {}
        
        for webhook in webhooks:
            try:
                response = requests.get(webhook, timeout=10)
                results[webhook] = {
                    'status': 'accessible' if response.status_code not in [403, 503] else 'blocked',
                    'response_code': response.status_code,
                    'response_time_ms': response.elapsed.total_seconds() * 1000
                }
                
            except Exception as e:
                results[webhook] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        return results
    
    def run_complete_fix(self) -> Dict:
        """Run complete Cloudflare configuration fix"""
        
        print("🔧 FIXING CLOUDFLARE CONFIGURATION FOR SPOOKYJUICE AI")
        print("=" * 55)
        
        results = {
            'timestamp': time.time(),
            'steps': {}
        }
        
        # Step 1: Verify access
        if not self.verify_access():
            return {'error': 'API access verification failed'}
        
        # Step 2: Create IP rules
        print("\n📡 Creating Twilio IP access rules...")
        results['steps']['ip_rules'] = self.create_twilio_ip_rules()
        
        # Step 3: Create page rules
        print("\n📄 Creating webhook page rules...")
        results['steps']['page_rules'] = self.create_voice_webhook_rules()
        
        # Step 4: Test accessibility
        print("\n🧪 Testing webhook accessibility...")
        time.sleep(5)  # Wait for changes to propagate
        results['steps']['accessibility_test'] = self.test_webhook_accessibility()
        
        # Summary
        total_ip_rules = len(results['steps']['ip_rules']['created_rules'])
        total_page_rules = len(results['steps']['page_rules']['created_rules']) 
        accessible_webhooks = len([w for w in results['steps']['accessibility_test'].values() if w.get('status') == 'accessible'])
        
        results['summary'] = {
            'ip_rules_created': total_ip_rules,
            'page_rules_created': total_page_rules,
            'accessible_webhooks': accessible_webhooks,
            'configuration_successful': accessible_webhooks >= 1
        }
        
        print("\n✅ CLOUDFLARE CONFIGURATION COMPLETE!")
        print(f"IP rules created: {total_ip_rules}")
        print(f"Page rules created: {total_page_rules}")
        print(f"Accessible webhooks: {accessible_webhooks}/3")
        
        return results

def main():
    """Main function to run Cloudflare fixes"""
    
    api_token = os.getenv('CLOUDFLARE_API_TOKEN')
    zone_id = os.getenv('CLOUDFLARE_ZONE_ID')
    
    if not api_token or not zone_id:
        print("❌ ERROR: Missing Cloudflare credentials")
        print("Set these environment variables:")
        print("  export CLOUDFLARE_API_TOKEN=your_token")
        print("  export CLOUDFLARE_ZONE_ID=your_zone_id")
        return
    
    fixer = CloudflareFixer(api_token, zone_id)
    results = fixer.run_complete_fix()
    
    # Save results for reference
    with open('cloudflare_fix_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: cloudflare_fix_results.json")

if __name__ == "__main__":
    main()