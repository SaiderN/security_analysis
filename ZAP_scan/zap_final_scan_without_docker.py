#!/usr/bin/env python3
import requests
import json
import time
import sys
from datetime import datetime

def zap_api(endpoint):
    url = f"http://localhost:8080{endpoint}"
    try:
        response = requests.get(url, timeout=30)
        return response.json()
    except:
        return None

def get_alerts_count():
    """Get current number of alerts"""
    alerts = zap_api("/JSON/core/view/alerts/?baseurl=http://localhost:3000")
    if alerts and 'alerts' in alerts:
        return len(alerts['alerts'])
    return 0

def main():
    print("ZAP SCAN COMPARISON: SPIDER vs ACTIVE")
    print("=" * 50)
    
    target = "http://localhost:3000"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    

    version = zap_api("/JSON/core/view/version")
    if not version:
        print(" ZAP не запущен")
        sys.exit(1)
    
    print(f" ZAP {version.get('version')}")
    

    print(f"\n ШАГ 1: Начальное состояние")
    initial_count = get_alerts_count()
    print(f"   Уязвимостей до сканирования: {initial_count}")
    

    print(f"\n ШАГ 2: ЗАПУСК SPIDER SCAN...")
    spider = zap_api(f"/JSON/spider/action/scan/?url={target}")
    
    if spider and 'scan' in spider:

        for i in range(20):
            status = zap_api("/JSON/spider/view/status")
            if status and status.get('status') == '100':
                break
            time.sleep(5)
    

    spider_count = get_alerts_count()
    spider_new_vulns = spider_count - initial_count
    print(f"    Spider завершен")
    print(f"    Новых уязвимостей после Spider: {spider_new_vulns}")
    print(f"    Всего уязвимостей: {spider_count}")
    

    print(f"\n ШАГ 3: ЗАПУСК ACTIVE SCAN...")
    active = zap_api(f"/JSON/ascan/action/scan/?url={target}")
    
    if active and 'scan' in active:
        active_id = active['scan']
        print(f"   Active Scan ID: {active_id}")
        print("   Ждем 10 минут...")
        

        for i in range(60):
            status = zap_api(f"/JSON/ascan/view/status/?scanId={active_id}")
            if status and 'status' in status:
                progress = status['status']
                current_count = get_alerts_count()
                print(f"   Progress: {progress}% | Уязвимостей: {current_count}")
                
                if progress == '100':
                    break
            time.sleep(10)
    

    final_count = get_alerts_count()
    active_new_vulns = final_count - spider_count
    
    print(f"\n ИТОГОВАЯ СТАТИСТИКА:")
    print("=" * 40)
    print(f"  Начальное состояние: {initial_count}")
    print(f"  После Spider Scan:   {spider_count} (+{spider_new_vulns})")
    print(f"  После Active Scan:   {final_count} (+{active_new_vulns})")
    print("=" * 40)
    print(f"  Spider нашел:  {spider_new_vulns} уязвимостей")
    print(f"  Active нашел:  {active_new_vulns} уязвимостей")
    print(f"  Всего:         {final_count} уязвимостей")
    

    alerts = zap_api(f"/JSON/core/view/alerts/?baseurl={target}")
    
    with open(f"zap_comparison_{timestamp}.txt", "w", encoding='utf-8') as f:
        f.write("ZAP SCAN COMPARISON REPORT\n")
        f.write("=" * 50 + "\n")
        f.write(f"Initial vulnerabilities: {initial_count}\n")
        f.write(f"After Spider: {spider_count} (+{spider_new_vulns})\n")
        f.write(f"After Active: {final_count} (+{active_new_vulns})\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("ALL VULNERABILITIES:\n")
        f.write("-" * 50 + "\n")
        
        if alerts and 'alerts' in alerts:
            for i, vuln in enumerate(alerts['alerts'], 1):
                f.write(f"{i}. {vuln.get('name')}\n")
                f.write(f"   Risk: {vuln.get('risk')}\n")
                f.write(f"   URL: {vuln.get('url')}\n")
                f.write("-" * 30 + "\n")
    
    print(f"\n Полный отчет сохранен: zap_comparison_{timestamp}.txt")

if __name__ == "__main__":
    main()
