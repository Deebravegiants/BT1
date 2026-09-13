# [H] Arcane has Unauthenticated SSRF with Conditional Response Reflection in Template Fetch Endpoint

## Summary
Severity: High
Advisory: GHSA-ff24-4prj-gpmj
CVE: CVE-2026-40242
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-ff24-4prj-gpmj
Type: github-advisory

## Affected
- Go: `github.com/getarcaneapp/arcane/backend` — affected >=0 <1.17.3

## Details
### Summary
The /api/templates/fetch endpoint accepts a caller-supplied url parameter and performs a server-side HTTP GET request to that URL without authentication and without URL scheme or host validation. The server's response is returned directly to the caller. type. This constitutes an unauthenticated SSRF vulnerability affecting any publicly reachable Arcane instance.

### Details
- No allowlist or denylist of destination hosts/CIDRs
- No requirement for the caller to be authenticated

Response handling produces four distinct outcomes observable by the caller: 
- Valid JSON targets return a fully reflected response body if the returned fields fit the expected internal struct
- Non-JSON HTTP 200 responses produce an error leaking the first byte of the response (`"Invalid JSON response: invalid character '<'..."`)
- Non-200 responses leak the HTTP status code
- TCP-level failures distinguish between closed ports (`"connection refused"`) and filtered ones (`"i/o timeout"`)

### PoC
Send an unauthenticated GET request to `/api/templates/fetch`, passing the target URL as the `url` query parameter.

<img width="1041" height="375" alt="image" src="https://github.com/user-attachments/assets/f9fd475e-90b0-4dec-95e1-0af6263f5bb5" />

### Impact
- Unauthenticated port scanning of internal networks
- Access to internal HTTP services not exposed to the public internet (service discovery endpoints, internal dashboards, Kubernetes API)

## References
- https://github.com/getarcaneapp/arcane/security/advisories/GHSA-ff24-4prj-gpmj
- https://nvd.nist.gov/vuln/detail/CVE-2026-40242
- https://github.com/getarcaneapp/arcane
- https://github.com/getarcaneapp/arcane/releases/tag/v1.17.3
