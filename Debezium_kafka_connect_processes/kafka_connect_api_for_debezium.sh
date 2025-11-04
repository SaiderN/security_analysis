#!/bin/bash
for pid in $(ps aux | grep kafka | grep -v grep | awk '{print $2}'); do
    port=$(ps -p $pid -o args= | grep -oE 'port[ =][0-9]+' | grep -oE '[0-9]+' | head -1)
    [ -z "$port" ] && port=8083
    curl -s "http://localhost:$port/connector-plugins" | grep -q debezium && echo "PID $pid: YES" || echo "PID $pid: NO"
done