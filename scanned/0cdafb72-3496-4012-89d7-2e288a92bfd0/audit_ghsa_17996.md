# [M] Microweber XSS Vulnerability in the homepage Endpoint 

## Summary
Severity: Medium
Advisory: GHSA-2x2j-3c2v-g3c2
CVE: CVE-2025-51504
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2025-08-01
Source: https://github.com/advisories/GHSA-2x2j-3c2v-g3c2
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=2.0.0

## Details
Microweber CMS 2.0 is vulnerable to Cross Site Scripting (XSS) in the /projects/profile, homepage endpoint via the last name field.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-51504
- https://github.com/microweber/microweber
- https://github.com/progprnv/CVE-Reports
- https://github.com/progprnv/CVE-Reports/blob/main/CVE-2025-51504
- https://github.com/progprnv/CVE-Reports/blob/main/MICROWEBER%20%5BLive%20Panel%5D%20Stored%20XSS%20in%20profile%20path.md
