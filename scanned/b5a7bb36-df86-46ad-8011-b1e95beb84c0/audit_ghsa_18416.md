# [M] Harbor repository description page has Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-f9vc-vf3r-pqqq
CVE: CVE-2025-32019
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-23
Source: https://github.com/advisories/GHSA-f9vc-vf3r-pqqq
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=2.12.0-rc1 <2.12.4-rc1
- Go: `github.com/goharbor/harbor` — affected >=2.13.0-rc1 <2.13.1-rc1
- Go: `github.com/goharbor/harbor` — affected >=2.4.0-rc1.1
- Go: `github.com/goharbor/harbor` — affected >=0 <2.4.0-rc1.0.20250421072404-a13a16383a41

## Details
### Impact

In the Harbor repository information, it is possible to inject code resulting in a stored XSS issue.

### Patches
Harbor v2.12.3 Harbor 2.11.3

### Workarounds
No

### References

### Credit
gleb.razvitie@gmail.com

## References
- https://github.com/goharbor/harbor/security/advisories/GHSA-f9vc-vf3r-pqqq
- https://nvd.nist.gov/vuln/detail/CVE-2025-32019
- https://github.com/goharbor/harbor/commit/76c2c5f7cfd9edb356cbb373889a59cc3217a058
- https://github.com/goharbor/harbor/commit/a13a16383a41a8e20f524593cb290dc52f86f088
- https://github.com/goharbor/harbor/commit/f019430872118852f83f96cac9c587b89052d1e5
- https://github.com/goharbor/harbor
