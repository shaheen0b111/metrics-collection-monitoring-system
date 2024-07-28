''' pip3 install psutil, prometheus_client
    psutil docs : https://psutil.readthedocs.io/en/latest/
    prometheus_client docs: https://prometheus.github.io/client_python/
'''

import psutil, time
from prometheus_client import Gauge, start_http_server
import os,sys


# Define prometheus gauge metrics object 
gauge_cpu_usage = Gauge("gauge_cpu_usage","System CPU Usage in percent",['type'])
gauge_memory_usage = Gauge("gauge_mem_usage","System Memory Usage in percent",['type'])
gauge_disk_usage = Gauge("gauge_disk_usage","System Disk Usage in percent",['type'])


#Function that collect metrics
def fetch_metrics(interval_gap):
    print("Fetching Metrics - CPU, Memory, Disk")
    #fetch cpu usage in percentage using psutil
    cpu_usage_percent = psutil.cpu_percent()
    mem_usage_percent =  psutil.virtual_memory().percent
    disk_usage_percent =  psutil.disk_usage('/').percent

    # Set the prometheus gauge object with the metrics value fetched
    gauge_cpu_usage.labels(type='CPU').set(cpu_usage_percent)
    gauge_memory_usage.labels(type='Memory').set(mem_usage_percent)
    gauge_disk_usage.labels(type='').set(disk_usage_percent)
    time.sleep(interval_gap)

if __name__ == "__main__":
    # Get interval at run time
    interval_gap = sys.argv[1]
    #start prometheus HTTP server on port 8080
    print("Staring Prometheus Server on 8080 : http://localhost:8080/metrics")
    start_http_server(8080)

    while True:
        fetch_metrics(int(interval_gap))
        



