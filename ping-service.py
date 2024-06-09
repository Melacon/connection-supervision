################################################################################
# Copyright 2024 highstreet technologies USA Corp. and others
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import os
import time
import subprocess

from influxdb import InfluxDBClient

DELAY = int(os.getenv("DELAY", 10))
TARGET = os.getenv("TARGET", "google.com")

def ping(target):
    result = subprocess.run(["ping", "-c", "4", target], stdout=subprocess.PIPE)
    output = result.stdout.decode()
    return output

def parse_ping_output(output):
    lines = output.split("\n")
    summary = lines[-3:]
    return "\n".join(summary)

def send_to_influxdb(client, target, summary):
    data = []
    for line in summary.split("\n"):
        if "time=" in line:
            time_ms = line.split("time=")[-1].split(" ")[0]
            data.append({
                "measurement": "ping",
                "tags": {
                    "target": target
                },
                "fields": {
                    "response_time_ms": float(time_ms)
                }
            })
    client.write_points(data)

if __name__ == "__main__":
    client = InfluxDBClient(host='influxdb', port=8086)
    client.create_database('ping_data')
    client.switch_database('ping_data')

    while True:
        output = ping(TARGET)
        summary = parse_ping_output(output)
        send_to_influxdb(client, TARGET, summary)
        time.sleep(DELAY)
