#!/usr/bin/python3

import subprocess
from signal import signal, SIGINT
import datetime
import time,sys
import random
import re


resolvconf = '/etc/resolv.conf'
run_once_per = 3600

class DnsRequest():
    def __init__(self,server):
        self.server = server
    def __dns_query_results__(self):
        try:
            executable = "dig"
            site_query = "meraki.com"
            process = subprocess.Popen([executable, site_query, self.server],
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            dig_results = stdout.decode('utf-8')
            return dig_results
        except:
            sys.stderr("Unable to get DNS query results for {site} against {server}".format(site=site_query,server=self.server))

    def __process_results__(self):
        try:
            calendar = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Nov','Dec']
            query_time = []
            date = []
            answer = []
            month = 0
            for i in DnsRequest.__dns_query_results__(self).splitlines():
                if re.search("Query time:", i):
                    query_time.append(i.split())
                elif re.search("WHEN:", i):
                    date.append(i.lstrip(';; WHEN: '))
                elif re.search("ANSWER:", i):
                    answer.append(int(i.split()[8].rstrip(',')))
            date = date[0].split()
            current_day = int(date[2])
            current_time = date[3].split(":")
            hour = int(current_time[0])
            minute = int(current_time[1])
            second = int(current_time[2])
            tz = date[4]
            current_year = int(date[5])
            for index,month in enumerate(calendar):
                if date[1] in month:
                    month_num = index + 1
            if answer[0] > 0:
                response = "succeeded"
            else:
                response = "failed"
            self.query_time = query_time[0][3]
            ts= datetime.datetime(current_year, month_num, current_day, hour, minute, second).strftime('%s')
            if answer[0] > 0:
                full_response = ts+","+self.server+","+response+","+str(self.query_time)
            else:
                full_response = ts+","+self.server+","+response+","
            return full_response
        except:
            sys.stderr("An error occured while processing your query response.")

def get_nameservers():
        file = open(resolvconf, "r")
        name_server_list = []
        for i in file.readlines():
            if re.search(r'^#',i):
                pass
            elif re.search(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}', i):
                name_server_list.append(i.rstrip('\n'))
        return name_server_list
def handler(signal_received, frame):
    print("SIGINT or Ctrl-C detected. Exiting gracefully...")
    sys.exit(0)

if __name__ == '__main__':
    signal(SIGINT, handler)
    while True:
        try:
            rando_server = random.choice(get_nameservers())
            sleep_range = ((run_once_per / get_nameservers().__len__()) / 2)
            requestor = DnsRequest(rando_server)
            print(requestor.__process_results__())
            time.sleep(random.randrange(1,sleep_range))
        except:
            sys.stderr("Unable to complete DNS check against {server}.".format(server=rando_server))
