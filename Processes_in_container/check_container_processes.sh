#!/bin/bash

INIT_NS=$(readlink /proc/1/ns/net)

echo "USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND"

for pid in /proc/[0-9]*; do
    pid_num=$(basename "$pid")
    
    if [[ -f "/proc/$pid_num/ns/net" ]]; then
        current_ns=$(readlink "/proc/$pid_num/ns/net")

        process_info=$(ps -p "$pid_num" -o user=,pid=,pcpu=,pmem=,vsz=,rss=,tty=,stat=,start=,time=,cmd= --no-headers 2>/dev/null)
        
        if [[ -n "$process_info" ]]; then
            if [[ "$current_ns" != "$INIT_NS" ]]; then
                container_procs+=("$process_info")
            else
                echo "$process_info"
            fi
        fi
    fi
done

echo ""
for proc in "${container_procs[@]}"; do
    echo "Process running in the container ---> $proc"
done
echo ""