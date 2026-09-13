# [M] Gomatrixserverlib Server-Side Request Forgery (SSRF) on redirects and federation

## Summary
Severity: Medium
Advisory: GHSA-4ff6-858j-r822
CVE: CVE-2024-52594
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-01-16
Source: https://github.com/advisories/GHSA-4ff6-858j-r822
Type: github-advisory

## Affected
- Go: `github.com/matrix-org/gomatrixserverlib` — affected >=0 <0.0.0-20250116181547-c4f1e01eab0d

## Details
### Impact
Gomatrixserverlib is vulnerable to server-side request forgery, serving content from a private network it can access, under certain conditions.

### Patches

c4f1e01eab0dd435709ad15463ed38a079ad6128 fixes this issue.


### Workarounds
Use a local firewall to limit the network segments and hosts the service using gomatrixserverlib can access.

### References
N/A

## References
- https://github.com/matrix-org/gomatrixserverlib/security/advisories/GHSA-4ff6-858j-r822
- https://nvd.nist.gov/vuln/detail/CVE-2024-52594
- https://github.com/matrix-org/gomatrixserverlib/commit/c4f1e01eab0dd435709ad15463ed38a079ad6128
- https://github.com/matrix-org/gomatrixserverlib
- https://pkg.go.dev/vuln/GO-2025-3396
