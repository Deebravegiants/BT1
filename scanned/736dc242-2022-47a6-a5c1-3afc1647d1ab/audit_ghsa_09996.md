# [M] Pimcore has an authenticated Cross-site Scripting issue

## Summary
Severity: Medium
Advisory: GHSA-7gxw-q9j5-mrj4
CVE: CVE-2026-5362
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-04-27
Source: https://github.com/advisories/GHSA-7gxw-q9j5-mrj4
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected 12.3.3

## Details
An authenticated attacker with permission to edit document content can store crafted HTML/JavaScript in a Document embed editable and cause script execution when the published page is rendered.

This issue affects pimcore: v12.3.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-5362
- https://fluidattacks.com/es/advisories/mago
- https://github.com/pimcore/pimcore
