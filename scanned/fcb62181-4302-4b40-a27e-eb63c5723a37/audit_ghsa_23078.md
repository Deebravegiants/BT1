# [M] Joomla! XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g3m5-vvj7-xrwv
CVE: CVE-2018-11326
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-g3m5-vvj7-xrwv
Type: github-advisory

## Affected
- Packagist: `joomla/joomla-cms` — affected >=3.0.0 <3.8.8

## Details
An issue was discovered in Joomla! Core starting in 3.0.0 and prior to 3.8.8. Inadequate input filtering leads to a multiple XSS vulnerabilities. Additionally, the default filtering settings could potentially allow users of the default Administrator user group to perform a XSS attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11326
- https://developer.joomla.org/security-centre/733-20180505-core-xss-vulnerabilities-additional-hadering.html
- https://github.com/joomla/joomla-cms
- https://web.archive.org/web/20210124173032/http://www.securityfocus.com/bid/104270
- https://web.archive.org/web/20211129145422/http://www.securitytracker.com/id/1040966
