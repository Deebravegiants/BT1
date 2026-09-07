# [M] Subrion CMS XSS

## Summary
Severity: Medium
Advisory: GHSA-xvgx-668j-f67p
CVE: CVE-2019-20389
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xvgx-668j-f67p
Type: github-advisory

## Affected
- Packagist: `intelliants/subrion` — affected >=0

## Details
An XSS issue was identified on the Subrion CMS 4.2.1 /panel/configuration/general settings page. A remote attacker can inject arbitrary JavaScript code in the `v[language_switch]` parameter (within multipart/form-data), which is reflected back within a user's browser without proper output encoding.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-20389
- https://github.com/intelliants/subrion
- http://packetstormsecurity.com/files/157699/Subrion-CMS-4.2.1-Cross-Site-Scripting.html
