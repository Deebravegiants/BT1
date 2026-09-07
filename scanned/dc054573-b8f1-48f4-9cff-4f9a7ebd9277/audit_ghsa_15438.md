# [M] In regclient, pinned manifest digests may be ignored

## Summary
Severity: Medium
Advisory: GHSA-qv35-3gw6-8q4j
CVE: CVE-2025-24882
CWE: CWE-20, CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-qv35-3gw6-8q4j
Type: github-advisory

## Affected
- Go: `github.com/regclient/regclient` — affected >=0 <0.7.1

## Details
### Impact
A malicious registry could return a different digest for a pinned manifest without detection.

### Patches
This has been fixed in the v0.7.1 release.

### Workarounds
After running a `regclient.ManifestGet`, the returned digest can be compared to the requested digest.

## References
- https://github.com/regclient/regclient/security/advisories/GHSA-qv35-3gw6-8q4j
- https://nvd.nist.gov/vuln/detail/CVE-2025-24882
- https://github.com/regclient/regclient/commit/7d17cff26c22196b5ddd66bda8c5ee4abf3d1269
- https://github.com/regclient/regclient
- https://pkg.go.dev/vuln/GO-2024-3038
