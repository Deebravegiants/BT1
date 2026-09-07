# [H] lite-server vulnerable to Denial of Service

## Summary
Severity: High
Advisory: GHSA-89w7-5q45-r53w
CVE: CVE-2022-25940
CWE: CWE-20, CWE-400
Ecosystem: Maven, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-20
Source: https://github.com/advisories/GHSA-89w7-5q45-r53w
Type: github-advisory

## Affected
- npm: `lite-server` — affected >=0
- Maven: `org.webjars.npm:lite-server` — affected >=0

## Details
All versions of package lite-server are vulnerable to Denial of Service (DoS) when an attacker sends an HTTP request and includes control characters that the `decodeURI()` function is unable to parse.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25940
- https://gist.github.com/lirantal/832382155e00da92bfd8bb3adea474eb
- https://github.com/johnpapa/lite-server
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-3175617
- https://security.snyk.io/vuln/SNYK-JS-LITESERVER-3153540
