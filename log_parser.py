# -*- coding: utf-8 -*-
import re
import json
from argparse import ArgumentParser
from os import path, listdir
from collections import Counter
from sortedcontainers import SortedList

parser = ArgumentParser()
parser.add_argument('-f', '--file_path', type=str, dest='file', action='store',
                    help='Full path to logfile or dir with it')
parser.add_argument('-s', '--save_to', type=str, dest='save', action='store',
                    default='', help='Full path to logfile or dir with it')
args = parser.parse_args()

file_to_exec = []
if path.isdir(args.file):
    file_to_exec = [path.join(args.file, f) for f in listdir(args.file) if path.isfile(path.join(args.file, f))]
else:
    file_to_exec.append(args.file)

all_req = Counter()
req_by_method = Counter()
client_err_req = Counter()
server_err_req = Counter()
# костыль для инициализации отсортированного списка с 10 значениям чтобы в дальнейшем
# на каждой итерации добавлять и удалять по одному значению поддерживая длину списка == 10
list_template = [("0", "0", "0", "0")] * 10
exec_time_req = SortedList(list_template, key=lambda x: x[3])
cursed_lines = list()

for log in file_to_exec:
    with open(log, 'r') as file:
        for line in file:
            try:
                ip = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line).group(0)
                method, url = re.search(r'(GET|POST|PUT|DELETE|HEAD|OPTIONS|PROPFIND) \S+', line).group(0).split(' ')
                time = re.search(r'\d{1,2}/\w+/\d{4}:\d{2}:\d{2}:\d{2}', line).group(0)
                protocol = re.search(r'HTTPS?/\d.\d', line).group(0)
                path, status_code = re.search(r'HTTP/\d.\d\" [1-5]\d{2}', line).group(0).split('" ')
                exec_time = re.search(r'\d+$', line).group(0)
            except AttributeError as e:
                print(f"ERROR - {e.args} occurred while parsing the line - {line}")
                cursed_lines.append(line)
                continue

            all_req[ip] += 1

            req_by_method[method] += 1

            if status_code.startswith('4'):
                client_err_req[(ip, path, method, status_code)] += 1

            elif status_code.startswith('5'):
                server_err_req[(ip, path, method, status_code)] += 1

            exec_time_req.add((ip, path, method, exec_time))
            del exec_time_req[0]

result = {'total_requests': sum(all_req.values()),
          'requests_by_methods': dict(req_by_method),
          'top_10_most_common_ip': all_req.most_common(10),
          'top_10_longest_execution_time': list(exec_time_req),
          'top_10_requests_with_client_error': client_err_req.most_common(10),
          'top_10_requests_with_server_error': server_err_req.most_common(10),
          'lines_with_an_error': cursed_lines}
json_object = json.dumps(result, indent=4)

with open(args.save or 'result.json', 'w') as res:
    res.write(json_object)
