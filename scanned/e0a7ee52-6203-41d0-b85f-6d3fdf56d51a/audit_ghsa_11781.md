# [H] Traefik: Deny Rule Bypass via Unauthenticated Malicious gRPC Requests in gRPC-Go Dependency (CVE-2026-33186)

## Summary
Severity: High
Advisory: GHSA-46wh-3698-f2cx
CWE: CWE-1395, CWE-285
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-46wh-3698-f2cx
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.42
- Go: `github.com/traefik/traefik/v3` — affected >=3.0.0-beta3 <3.6.12
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0-ea.1 <3.7.0-ea.3

## Details
## Summary

There is a potential vulnerability in Traefik due to its dependency on an affected version of gRPC-Go (CVE-2026-33186).

A remote, unauthenticated attacker can send gRPC requests with a malformed HTTP/2 `:path` pseudo-header omitting the mandatory leading slash (e.g., `Service/Method` instead of `/Service/Method`). While the server routes such requests correctly, path-based authorization interceptors evaluate the raw non-canonical path and fail to match "deny" rules, allowing the request to bypass the policy entirely if a fallback "allow" rule is present.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.42
- https://github.com/traefik/traefik/releases/tag/v3.6.12
- https://github.com/traefik/traefik/releases/tag/v3.7.0-ea.3

## For more information

If there are any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

### Summary
This CVE hits traefik until Version 3.6.11 and 2.11.41.
gRPC-Go has an authorization bypass via missing leading slash in :path
### Details
As described in https://github.com/advisories/GHSA-p77j-4mvh-x3m3
### PoC
Update library version in 
https://github.com/traefik/traefik/blob/67c64ed9b25fbb90f1086977a62827133a7aa01b/go.mod#L108
### Impact
Is described in https://github.com/advisories/GHSA-p77j-4mvh-x3m3

</details>


----------

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-46wh-3698-f2cx
- https://github.com/advisories/GHSA-p77j-4mvh-x3m3
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/blob/67c64ed9b25fbb90f1086977a62827133a7aa01b/go.mod#L108
- https://github.com/traefik/traefik/releases/tag/v2.11.42
- https://github.com/traefik/traefik/releases/tag/v3.6.12
- https://github.com/traefik/traefik/releases/tag/v3.7.0-ea.3
