# [M] PHP League CommonMark vulnerable to Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-qx76-c53f-5c7q
CVE: CVE-2018-20583
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qx76-c53f-5c7q
Type: github-advisory

## Affected
- Packagist: `league/commonmark` — affected >=0.15.6 <0.18.1

## Details
Cross-site scripting (XSS) vulnerability in the PHP League CommonMark library versions 0.15.6 through 0.18.x before 0.18.1 allows remote attackers to insert unsafe URLs into HTML (even if allow_unsafe_links is false) via a newline character (e.g., writing javascript as javascri%0apt).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20583
- https://github.com/thephpleague/commonmark/issues/337
- https://commonmark.thephpleague.com/changelog
- https://github.com/FriendsOfPHP/security-advisories/blob/master/league/commonmark/CVE-2018-20583.yaml
- https://github.com/thephpleague/commonmark
- https://github.com/thephpleague/commonmark/releases/tag/0.18.1
