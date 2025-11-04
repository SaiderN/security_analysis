#!/usr/bin/env python3
import subprocess
import json
import time
import sys

def docker_exec(endpoint):
    """Execute API call in ZAP container"""
    cmd = f'docker exec zap-api curl -s "http://localhost:8080{endpoint}"'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"API Error: {e}")
    return None

def wait_for_spider_completion():
    """Wait for spider to complete"""
    print("Waiting for spider to complete...")
    
    for i in range(60):  # Max 10 minutes
        status = docker_exec("/JSON/spider/view/status")
        if status and 'status' in status:
            progress = status['status']
            print(f"Spider progress: {progress}%")
            
            if progress == '100':
                print("Spider completed successfully!")
                return True
        time.sleep(10)
    
    print("Spider timeout reached, continuing with results...")
    return False

def get_all_alerts(target):
    """Get all security alerts"""
    alerts = docker_exec(f"/JSON/core/view/alerts/?baseurl={target}")
    if alerts and 'alerts' in alerts:
        return alerts['alerts']
    return []

def print_detailed_results(alerts):
    """Print all vulnerabilities with details"""
    print("\n" + "="*80)
    print("SPIDER SCAN RESULTS - ALL VULNERABILITIES")
    print("="*80)
    
    if not alerts:
        print("No vulnerabilities found.")
        return
    
    print(f"Total vulnerabilities found: {len(alerts)}\n")
    

    for i, alert in enumerate(alerts, 1):
        print(f"VULNERABILITY {i}:")
        print(f"  Name: {alert.get('name')}")
        print(f"  Risk: {alert.get('risk')}")
        print(f"  Confidence: {alert.get('confidence')}")
        print(f"  URL: {alert.get('url')}")
        
        if alert.get('param'):
            print(f"  Parameter: {alert.get('param')}")
        
        if alert.get('attack'):
            print(f"  Attack: {alert.get('attack')}")
        
        if alert.get('evidence'):
            print(f"  Evidence: {alert.get('evidence')}")
        
        print(f"  Description: {alert.get('description', 'N/A')}")
        
        if alert.get('solution'):
            print(f"  Solution: {alert.get('solution')}")
        
        if alert.get('reference'):
            print(f"  Reference: {alert.get('reference')}")
        
        print(f"  CWE ID: {alert.get('cweid', 'N/A')}")
        print(f"  WASC ID: {alert.get('wascid', 'N/A')}")
        print("-" * 80)

def stop_and_cleanup():
    """Stop and remove ZAP container"""
    print("\nStopping and cleaning up container...")
    subprocess.run("docker stop zap-api", shell=True)
    subprocess.run("docker rm zap-api", shell=True)
    print("Container cleaned up successfully!")

def main():
    print("ZAP SPIDER SCAN ONLY")
    print("=" * 50)
    
    target = "http://localhost:3000"
    

    version = docker_exec("/JSON/core/view/version")
    if not version:
        print("Error: ZAP container is not accessible. Make sure it's running with name 'zap-api'")
        print("Start it with: docker run -d --name zap-api -p 8080:8080 zaproxy/zap-stable zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true")
        sys.exit(1)
    
    print(f"ZAP Version: {version.get('version')}")
    

    print(f"\nStarting spider scan of {target}...")
    spider_result = docker_exec(f"/JSON/spider/action/scan/?url={target}")
    
    if not spider_result or 'scan' not in spider_result:
        print("Failed to start spider scan")
        stop_and_cleanup()
        sys.exit(1)
    
    print(f"Spider started with ID: {spider_result['scan']}")
    

    if not wait_for_spider_completion():
        print("Spider did not complete within timeout")
    

    print("\nCollecting all vulnerabilities...")
    alerts = get_all_alerts(target)
    

    print_detailed_results(alerts)
    

    stop_and_cleanup()
    
    print(f"\nSpider scan completed. Found {len(alerts) if alerts else 0} vulnerabilities.")

if __name__ == "__main__":
    main()
