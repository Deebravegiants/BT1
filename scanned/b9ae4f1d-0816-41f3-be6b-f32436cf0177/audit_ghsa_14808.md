# [C] Jan path traversal vulnerability

## Summary
Severity: Critical
Advisory: GHSA-qfjh-mvq6-c5p8
CVE: CVE-2024-36858
CWE: CWE-434
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-qfjh-mvq6-c5p8
Type: github-advisory

## Affected
- npm: `@janhq/core` — affected >=0

## Details
An arbitrary file upload vulnerability in the /v1/app/writeFileSync interface of Jan v0.4.12 allows attackers to execute arbitrary code via uploading a crafted file. @janhq/core has been deprecated in favor of janhq/jan, this vulnerability has been patched there in v0.5.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36858
- https://github.com/janhq/jan/pull/3152
- https://github.com/HackAllSec/CVEs/tree/main/Jan%20Arbitrary%20File%20Upload%20vulnerability
- https://github.com/janhq/jan
