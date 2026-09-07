# [M] SimpleSAMLphp XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fv7m-wc3v-wr3w
CVE: CVE-2017-18121
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-fv7m-wc3v-wr3w
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp` — affected >=1.12.0 <1.14.16

## Details
The consentAdmin module in SimpleSAMLphp through 1.14.15 is vulnerable to a Cross-Site Scripting attack, allowing an attacker to craft links that could execute arbitrary JavaScript code on the victim's web browser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18121
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/simplesamlphp/CVE-2017-18121.yaml
- https://lists.debian.org/debian-lts-announce/2018/02/msg00008.html
- https://simplesamlphp.org/security/201709-01
- https://www.debian.org/security/2018/dsa-4127
