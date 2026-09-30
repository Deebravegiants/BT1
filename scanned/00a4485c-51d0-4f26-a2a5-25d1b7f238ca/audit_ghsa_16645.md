# [H] MiguelCastillo @bit/loader Prototype Pollution issue

## Summary
Severity: High
Advisory: GHSA-8vr4-h4rr-8ph6
CVE: CVE-2024-24293
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-8vr4-h4rr-8ph6
Type: github-advisory

## Affected
- npm: `@bit/loader` — affected >=0

## Details
A Prototype Pollution issue in MiguelCastillo @bit/loader v.10.0.3 allows an attacker to execute arbitrary code via the M function e argument in index.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24293
- https://gist.github.com/tariqhawis/986fb1c9da6be526fb2656ba8d194b7f
- https://github.com/MiguelCastillo/bit-loader
