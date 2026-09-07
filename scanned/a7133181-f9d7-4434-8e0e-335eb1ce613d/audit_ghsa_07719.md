# [M] WireGuard Portal v2 has Open Redirect Vulnerability in OAuth Authentication Flow

## Summary
Severity: Medium
Advisory: GHSA-grh9-37g7-53mj
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-grh9-37g7-53mj
Type: github-advisory

## Affected
- Go: `github.com/h44z/wg-portal` — affected >=0 <2.1.2

## Details
### Summary
An Open Redirect vulnerability exists in the OAuth authentication flow that allows attackers to redirect users to external malicious websites after authentication. The vulnerability is caused by insufficient validation of the return parameter in the OAuth login initialization endpoint.

### Patches
The problem was fixed in the latest release, v2.1.2. The [docker images](https://hub.docker.com/r/wgportal/wg-portal) for the tag 'latest' built from the master branch also include the fix.

## References
- https://github.com/h44z/wg-portal/security/advisories/GHSA-grh9-37g7-53mj
- https://github.com/h44z/wg-portal/commit/e62db0d62ebabbec39c767b953b92fb4b4d08a81
- https://github.com/h44z/wg-portal
- https://github.com/h44z/wg-portal/releases/tag/v2.1.2
