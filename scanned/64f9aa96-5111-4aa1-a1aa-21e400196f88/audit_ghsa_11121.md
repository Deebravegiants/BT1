# [M] Glances's REST/WebUI Lacks Host Validation and Remains Exposed to DNS Rebinding

## Summary
Severity: Medium
Advisory: GHSA-hhcg-r27j-fhv9
CVE: CVE-2026-32632
CWE: CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-hhcg-r27j-fhv9
Type: github-advisory

## Affected
- PyPI: `Glances` — affected >=0 <4.5.2

## Details
## Summary

Glances recently added DNS rebinding protection for the MCP endpoint, but the main REST/WebUI FastAPI application still accepts arbitrary `Host` headers and does not apply `TrustedHostMiddleware` or an equivalent host allowlist.

As a result, the REST API, WebUI, and token endpoint remain reachable through attacker-controlled domains in classic DNS rebinding scenarios. Once the victim browser has rebound the attacker domain to the Glances service, same-origin policy no longer protects the API because the browser considers the rebinding domain to be the origin.

This is a distinct issue from the previously reported default CORS weakness. CORS is not required for exploitation here because DNS rebinding causes the victim browser to treat the malicious domain as same-origin with the rebinding target.

## Details

The MCP endpoint now has explicit host-based transport security:

```python
# glances/outputs/glances_mcp.py
self.mcp_allowed_hosts = ["localhost", "127.0.0.1"]
...
return TransportSecuritySettings(
    allowed_hosts=allowed_hosts,
    allowed_origins=allowed_origins,
)
```

However, the main FastAPI application for REST/WebUI/token routes is initialized without any host validation middleware:

```python
# glances/outputs/glances_restful_api.py
self._app = FastAPI(default_response_class=GlancesJSONResponse)
...
self._app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get_list_value('outputs', 'cors_origins', default=["*"]),
    allow_credentials=config.get_bool_value('outputs', 'cors_credentials', default=True),
    allow_methods=config.get_list_value('outputs', 'cors_methods', default=["*"]),
    allow_headers=config.get_list_value('outputs', 'cors_headers', default=["*"]),
)
...
if self.args.password and self._jwt_handler is not None:
    self._app.include_router(self._token_router())
self._app.include_router(self._router())
```

There is no `TrustedHostMiddleware`, no comparison against the configured bind host, and no allowlist enforcement for HTTP `Host` values on the REST/WebUI surface.

The default bind configuration also exposes the service on all interfaces:

```python
# glances/main.py
parser.add_argument(
    '-B',
    '--bind',
    default='0.0.0.0',
    dest='bind_address',
    help='bind server to the given IPv4/IPv6 address or hostname',
)
```

This combination means the HTTP service will typically be reachable from the victim machine under an attacker-selected hostname once DNS is rebound to the Glances listener.

The token endpoint is also mounted on the same unprotected FastAPI app:

```python
# glances/outputs/glances_restful_api.py
def _token_router(self) -> APIRouter:
    ...
    router.add_api_route(f'{base_path}/token', self._api_token, methods=['POST'], dependencies=[])
```

## Why This Is Exploitable

In a DNS rebinding attack:

1. The attacker serves JavaScript from `https://attacker.example`.
2. The victim visits that page while a Glances instance is reachable on the victim network.
3. The attacker's DNS for `attacker.example` is rebound from the attacker's server to the Glances IP address.
4. The victim browser now sends same-origin requests to `https://attacker.example`, but those requests are delivered to Glances.
5. Because the Glances REST/WebUI app does not validate the `Host` header or enforce an allowed-host policy, it serves the response.
6. The attacker-controlled JavaScript can read the response as same-origin content.

The MCP code already acknowledges this threat model and implements host-level defenses. The REST/WebUI code path does not.

## Proof of Concept

This issue is code-validated by inspection of the current implementation:

- REST/WebUI/token are all mounted on a plain `FastAPI(...)` app
- no `TrustedHostMiddleware` or equivalent host validation is applied
- default bind is `0.0.0.0`
- MCP has separate rebinding protection, showing the project already recognizes the threat model

In a live deployment, the expected verification is:

```bash
# Victim-accessible Glances service
glances -w

# Attacker-controlled rebinding domain first resolves to attacker infra,
# then rebinds to the victim-local Glances IP.
# After rebind, attacker JS can fetch:
fetch("http://attacker.example:61208/api/4/status")
  .then(r => r.text())
  .then(console.log)
```

And if the operator exposes Glances without `--password` (supported and common), the attacker can read endpoints such as:

```bash
GET /api/4/status
GET /api/4/all
GET /api/4/config
GET /api/4/args
GET /api/4/serverslist
```

Even on password-enabled deployments, the missing host validation still leaves the REST/WebUI/token surface reachable through rebinding and increases the value of chains with other authenticated browser issues.

## Impact

- **Remote read of local/internal REST data:** DNS rebinding can expose Glances instances that were intended to be reachable only from a local or internal network context.
- **Bypass of origin-based browser isolation:** Same-origin policy no longer protects the API once the browser accepts the attacker-controlled rebinding host as the origin.
- **High-value chaining surface:** This expands the exploitability of previously identified Glances issues involving permissive CORS, credential-bearing API responses, and state-changing authenticated endpoints.
- **Token surface exposure:** The JWT token route is mounted on the same host-unvalidated app and is therefore also reachable through the rebinding path.

## Recommended Fix

Apply host allowlist enforcement to the main REST/WebUI FastAPI app, similar in spirit to the MCP hardening:

```python
from starlette.middleware.trustedhost import TrustedHostMiddleware

allowed_hosts = config.get_list_value(
    'outputs',
    'allowed_hosts',
    default=['localhost', '127.0.0.1'],
)

self._app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
```

At minimum:

- reject requests whose `Host` header does not match an explicit allowlist
- do not rely on `0.0.0.0` bind semantics as an access-control boundary
- document that reverse-proxy deployments must set a strict host allowlist

## References

- `glances/outputs/glances_mcp.py`
- `glances/outputs/glances_restful_api.py`
- `glances/main.py`

## References
- https://github.com/nicolargo/glances/security/advisories/GHSA-hhcg-r27j-fhv9
- https://nvd.nist.gov/vuln/detail/CVE-2026-32632
- https://github.com/nicolargo/glances/commit/5850c564ee10804fdf884823b9c210eb954dd1f9
- https://github.com/nicolargo/glances
- https://github.com/nicolargo/glances/releases/tag/v4.5.2
