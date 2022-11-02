# -*- encoding: utf-8 -*-
#
# pip install prometheus_client
#

from prometheus_client import start_http_server
from prometheus_client import Gauge
from prometheus_client import REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR

import time
import os
import sys
import re
import requests

# -------------------------------------------------------
# Reset metrics
# -------------------------------------------------------
def resetCacheState():
    GaugeUniParams.clear()

# -------------------------------------------------------
# Fetch and Parse
# -------------------------------------------------------
def get_html_body():
    try:
        r = requests.get(target_url)
        if r.status_code != 200:
            sys.exit('Error resp: %s' % r.status_code)
        return r.text

    except Exception as e:
        sys.stderr.write('error:'+str(e))
        exit(1)


def fetch_and_parse():
  sys.stdout.write("processing...\n")

  try:
    # Get all IPs
    resp = get_html_body()

    # Reset metrics
    resetCacheState()

    # prepare keys
    key_pattern = re.compile(r"var Ds= new Array\((.+?)\);", re.MULTILINE | re.DOTALL)
    val_data = key_pattern.search(resp)[1]
    keys = re.findall(r"new Array\('(.+?)'\)", val_data)

    # prepare vals
    values_pattern = re.compile(r"var V =new Array\((.+?)\);", re.MULTILINE | re.DOTALL)
    vals = values_pattern.search(resp)[1].replace('"', '').split(",")  

    i = 0
    for key in keys:
        GaugeUniParams.labels(key).set(vals[i])
        i = i + 1

  except Exception as e:
    sys.stderr.write('error:'+str(e))
    exit(1)

# -------------------------------------------------------
# MAIN
# -------------------------------------------------------
def main():

  # Start up the server to expose the metrics.
  start_http_server(port)

  # Generate some requests.
  while True:
      fetch_and_parse()
      time.sleep(interval)

# -------------------------------------------------------
# RUN
# -------------------------------------------------------

# http port - default 9299
port = int(os.getenv('PORT', 9299))

# Refresh interval between collects in seconds - default 60
interval = int(os.getenv('INTERVAL', 60))

target_ip = os.getenv('TARGET_IP', None)
target_port = int(os.getenv('TARGET_PORT', 80))
target_url = os.getenv('TARGET_URL', None)

# if not target_ip:
#   sys.stderr.write("Target IP is required please set TARGET_IP environment variable.\n")
#   exit(1)

# if not target_port:
#   sys.stderr.write("Target Port is required please set TARGET_PORT environment variable.\n")
#   exit(1)

if not target_url:
  sys.stderr.write("Target URL is required please set TARGET_URL environment variable.\n")
  exit(1)

# Show init parameters
sys.stdout.write('----------------------\n')
sys.stdout.write('Init parameters\n')
sys.stdout.write('port : ' + str(port) + '\n')
sys.stdout.write('interval : ' + str(interval) + 's\n')
# sys.stdout.write('target_ip : ' + str(target_ip) + '\n')
# sys.stdout.write('target_port : ' + str(target_port) + '\n')
sys.stdout.write('target_url : ' + str(target_url) + '\n')
sys.stdout.write('----------------------\n')

# Disable default python metrics
REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)

# Create gauge
GaugeUniParams = Gauge('unitronics_params', 'Unitronics Params', ['param'])

if __name__ == '__main__':
  main()
