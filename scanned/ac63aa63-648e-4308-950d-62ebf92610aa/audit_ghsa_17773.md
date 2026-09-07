# [M] matrix-media-repo (MMR) allows a denial of service through memory exhaustion

## Summary
Severity: Medium
Advisory: GHSA-gp86-q8hg-fpxj
CVE: CVE-2024-52791
CWE: CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-01-16
Source: https://github.com/advisories/GHSA-gp86-q8hg-fpxj
Type: github-advisory

## Affected
- Go: `github.com/t2bot/matrix-media-repo` — affected >=0 <1.3.8

## Details
### Impact
MMR makes requests to other servers as part of normal operation, and these resource owners can return large amounts of JSON back to MMR for parsing. In parsing, MMR can consume large amounts of memory and exhaust available memory.

### Patches
This is fixed in [MMR v1.3.8](https://github.com/t2bot/matrix-media-repo/releases/tag/v1.3.8).

### Workarounds
Forward proxies can be configured to block requests to unsafe hosts. Alternatively, MMR processes can be configured with memory limits and auto-restart. Running multiple MMR processes concurrently can help ensure a restart does not overly impact users.

## References
- https://github.com/t2bot/matrix-media-repo/security/advisories/GHSA-gp86-q8hg-fpxj
- https://nvd.nist.gov/vuln/detail/CVE-2024-52791
- https://github.com/t2bot/matrix-media-repo
- https://github.com/t2bot/matrix-media-repo/releases/tag/v1.3.8
- https://pkg.go.dev/vuln/GO-2025-3398
