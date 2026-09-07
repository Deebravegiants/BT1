# [M] Cross-site Scripting in Bagisto

## Summary
Severity: Medium
Advisory: GHSA-c962-g533-823f
CVE: CVE-2023-36236
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-01-17
Source: https://github.com/advisories/GHSA-c962-g533-823f
Type: github-advisory

## Affected
- Packagist: `bagisto/bagisto` — affected >=0 <1.3.2

## Details
Cross Site Scripting vulnerability in webkil Bagisto v1.3.1 and before allows an attacker to execute arbitrary code via a crafted SVG file uplad.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-36236
- https://github.com/bagisto/bagisto/pull/4764/commits/7bbf0c4bb565fc2601f031f9bbcdfa06e24dbd45
- https://github.com/bagisto/bagisto/commit/7bbf0c4bb565fc2601f031f9bbcdfa06e24dbd45
- https://bagisto.com/en
- https://github.com/Ek-Saini/security/blob/main/XSS_via_fileupload-bagisto
