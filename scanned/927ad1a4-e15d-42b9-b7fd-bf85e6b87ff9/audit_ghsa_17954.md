# [M] Microweber has Reflected XSS Vulnerability in the id Parameter

## Summary
Severity: Medium
Advisory: GHSA-8357-fjvx-xrm8
CVE: CVE-2025-51501
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-08-01
Source: https://github.com/advisories/GHSA-8357-fjvx-xrm8
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=2.0.0

## Details
Reflected Cross-Site Scripting (XSS) in the id parameter of the live_edit.module_settings API endpoint in Microweber CMS2.0 allows execution of arbitrary JavaScript.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-51501
- https://github.com/microweber/microweber
- https://github.com/progprnv/CVE-Reports
- https://github.com/progprnv/CVE-Reports/blob/main/CVE-2025-51501
- https://github.com/progprnv/CVE-Reports/blob/main/MICROWEBER%20%5BAdmin%20Panel%5D%20Reflected%20XSS%20on%20id%20parameter.md
