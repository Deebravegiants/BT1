# [H] melange: Incomplete package integrity verification allows data section substitution

## Summary
Severity: High
Advisory: GHSA-fpg8-7664-jc5q
CVE: CVE-2026-54174
CWE: CWE-345, CWE-354
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-fpg8-7664-jc5q
Type: github-advisory

## Affected
- Go: `chainguard.dev/apko` — affected >=0 <1.2.9
- Go: `chainguard.dev/melange` — affected >=0 <0.50.4

## Details
Previously, Apko verified the control section hash (`.PKGINFO` etc.) against the signed `APKINDEX`, but never verified the data section hash (the actual package files that get installed). An attacker who could compromise a mirror, poison a cache, or MITM a package fetch could substitute arbitrary file contents while the control hash check still passed.

## References
- https://github.com/chainguard-dev/melange/security/advisories/GHSA-fpg8-7664-jc5q
- https://github.com/chainguard-dev/melange
