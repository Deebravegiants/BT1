# [H] Cross-Site Request Forgery in Vert.x-Web framework

## Summary
Severity: High
Advisory: GHSA-9q69-g5gc-9fgf
CVE: CVE-2020-35217
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-22
Source: https://github.com/advisories/GHSA-9q69-g5gc-9fgf
Type: github-advisory

## Affected
- Maven: `io.vertx:vertx-web` — affected >=4.0.0-milestone1 <4.0.0-milestone5
- Maven: `io.vertx:vertx-web` — affected >=4.0.0-milestone2 <4.0.0-milestone5
- Maven: `io.vertx:vertx-web` — affected >=4.0.0-milestone3 <4.0.0-milestone5
- Maven: `io.vertx:vertx-web` — affected >=4.0.0-milestone4 <4.0.0-milestone5

## Details
Vert.x-Web framework v4.0 milestone 1-4 does not perform a correct CSRF verification. Instead of comparing the CSRF token in the request with the CSRF token in the cookie, it compares the CSRF token in the cookie against a CSRF token that is stored in the session. An attacker does not even need to provide a CSRF token in the request because the framework does not consider it. The cookies are automatically sent by the browser and the verification will always succeed, leading to a successful CSRF attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35217
- https://github.com/vert-x3/vertx-web/pull/1613
