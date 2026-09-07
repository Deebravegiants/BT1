# [M] PiranhaCMS stored XSS

## Summary
Severity: Medium
Advisory: GHSA-456v-f425-8mcv
CVE: CVE-2025-57692
CWE: CWE-79
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2025-09-26
Source: https://github.com/advisories/GHSA-456v-f425-8mcv
Type: github-advisory

## Affected
- NuGet: `Piranha` — affected >=0

## Details
PiranhaCMS 12.0 allows stored XSS in the Text content block of Standard and Standard Archive Pages via /manager/pages, enabling execution of arbitrary JavaScript in another user s browser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57692
- https://github.com/PiranhaCMS/piranha.core
- https://github.com/PiranhaCMS/piranha.core/releases/tag/v12.0
- https://github.com/Saconyfx/security-advisories/blob/main/CVE-2025-57692/advisory.md
