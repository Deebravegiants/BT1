# [H] Subrion CMS Cross-Site Request Forgery (CSRF) vulnerability

## Summary
Severity: High
Advisory: GHSA-c4wx-3x5q-hf4w
CVE: CVE-2019-20390
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c4wx-3x5q-hf4w
Type: github-advisory

## Affected
- Packagist: `intelliants/subrion` — affected 4.2.1

## Details
A Cross-Site Request Forgery (CSRF) vulnerability was discovered in Subrion CMS 4.2.1 that allows a remote attacker to remove files on the server without a victim's knowledge, by enticing an authenticated user to visit an attacker's web page. The application fails to validate the CSRF token for a GET request. An attacker can craft a panel/uploads/read.json?cmd=rm URL (removing this token) and send it to the victim.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-20390
- https://github.com/intelliants/subrion
- http://packetstormsecurity.com/files/157700/Subrion-CMS-4.2.1-Cross-Site-Request-Forgery.html
