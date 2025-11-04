#!/usr/bin/env python3
import subprocess
import json
import sys

def docker_exec(endpoint):
    """Execute API call in ZAP container"""
    cmd = f'docker exec zap-api curl -s "http://localhost:8080{endpoint}"'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except:
        return None

def list_assets():
    """List all assets in sites tree"""
    print("Current assets in ZAP:")
    print("-" * 50)
    

    sites = docker_exec("/JSON/core/view/sites/")
    if sites and 'sites' in sites:
        for site in sites['sites']:
            print(f"• {site}")
    else:
        print("No assets found")

def add_asset(target_url):
    """Add asset to scan by accessing it"""
    print(f"Adding asset: {target_url}")
    

    result = docker_exec(f"/JSON/core/action/accessUrl/?url={target_url}")
    if result and 'result' in result:
        print(f"Asset added successfully: {target_url}")
        

        spider_result = docker_exec(f"/JSON/spider/action/scan/?url={target_url}")
        if spider_result and 'scan' in spider_result:
            print(f"Spider started on new asset (ID: {spider_result['scan']})")
        return True
    else:
        print(f"Failed to add asset: {target_url}")
        return False

def remove_asset(target_url):
    """Remove asset from ZAP"""
    print(f"Removing asset: {target_url}")
    

    result = docker_exec(f"/JSON/core/action/deleteSiteNode/?url={target_url}")
    if result and 'result' in result:
        print(f"Asset removed: {target_url}")
        return True
    else:
        print(f"Failed to remove asset: {target_url}")
        return False

def clear_all_assets():
    """Clear all assets/sites"""
    print("Clearing all assets...")
    result = docker_exec("/JSON/core/action/deleteAllSiteNodes/")
    if result and 'result' in result:
        print("  All assets cleared")
        return True
    else:
        print("Failed to clear assets")
        return False

def main():
    print("ZAP ASSETS MANAGER")
    print("=" * 40)
    

    version = docker_exec("/JSON/core/view/version")
    if not version:
        print("Error: ZAP container is not running!")
        print("Start it with: docker run -d --name zap-api -p 8080:8080 zaproxy/zap-stable zap.sh -daemon -host 0.0.0.0 -port 8080 -config api.disablekey=true")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 zap_assets_manager.py list")
        print("  python3 zap_assets_manager.py add <URL>")
        print("  python3 zap_assets_manager.py remove <URL>") 
        print("  python3 zap_assets_manager.py clear")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        list_assets()
    
    elif command == "add" and len(sys.argv) == 3:
        add_asset(sys.argv[2])
    
    elif command == "remove" and len(sys.argv) == 3:
        remove_asset(sys.argv[2])
    
    elif command == "clear":
        clear_all_assets()
    
    else:
        print("Invalid command or missing parameters")

if __name__ == "__main__":
    main()