![Beamgun Infographic](https://github.com/JLospinoso/beamgun/raw/master/memcachedump.png)

`memcachedump` is a tool for dumping the cache contents of exposed memcached servers into local text files.

You'll need Python 2 or 3 and a [Shodan API Key](https://developer.shodan.io/api).

# Running the tool:

```
> python mcd.py --help
usage: mcd.py [-h] [--key KEY] [--out OUT] [--json]

Scrape data from memcached servers.

optional arguments:
  -h, --help  show this help message and exit
  --key KEY   Shodan API key.
  --out OUT   Output directory for caches.
  --json      Output as JSON. (Default: CSV)
```

You must supply your Shodan API `--key`. 

Optionally, you can specify an `--out` directory for the text files. By default, `mcd` writes to `./out`.

You can also specify `--json` output. By default, writes a CSV file.

# Prepping the environment

```
pip install shodan
```

