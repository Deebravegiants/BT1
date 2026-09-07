# [M] Pi Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9v3w-m552-m6ff
CVE: CVE-2017-7251
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-9v3w-m552-m6ff
Type: github-advisory

## Affected
- Packagist: `pi/pi` — affected >=0 <2.6.0-alpha1

## Details
A Cross-Site Scripting (XSS) was discovered in pi-engine/pi 2.5.0. The vulnerability exists due to insufficient filtration of user-supplied data (preview) passed to the `pi-develop/www/script/editor/markitup/preview/markdown.php` URL. An attacker could execute arbitrary HTML and script code in a browser in the context of the vulnerable website.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7251
- https://github.com/pi-engine/pi/issues/1523
- https://github.com/pi-engine/pi/commit/557cd05b21b4d7fe422f90adcfa0c6e3bea06153
- https://github.com/pi-engine/pi
- https://web.archive.org/web/20210124010656/https://www.securityfocus.com/bid/97061
