# [H] TYPO3 Remote Code Execution in extension "Site Crawler" (crawler)

## Summary
Severity: High
Advisory: GHSA-jr8m-x4p7-p3v5
CVE: CVE-2026-8727
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:A/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-jr8m-x4p7-p3v5
Type: github-advisory

## Affected
- Packagist: `tomasnorre/crawler` — affected >=12.0.0 <12.0.11
- Packagist: `tomasnorre/crawler` — affected >=0 <11.0.13

## Details
The TYPO3 Crawler extension passes the X-T3Crawler-Meta response header from crawled URLs directly to PHP's `unserialize()`. An attacker controlling a crawled endpoint can inject arbitrary serialized PHP objects, leading to Remote Code Execution on the TYPO3 server. Exploitation requires administrative privileges to configure a crawler-enabled page and trigger the crawl via a Scheduler task. This has been patched in versions 12.0.11 and 11.0.13.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8727
- https://github.com/FriendsOfPHP/security-advisories/blob/master/tomasnorre/crawler/CVE-2026-8727.yaml
- https://github.com/tomasnorre/crawler
- https://typo3.org/security/advisory/typo3-ext-sa-2026-008
