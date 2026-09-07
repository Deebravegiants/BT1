# [M] CSRF in Play Framework

## Summary
Severity: Medium
Advisory: GHSA-cf8j-64h9-6q58
CVE: CVE-2020-12480
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-08-18
Source: https://github.com/advisories/GHSA-cf8j-64h9-6q58
Type: github-advisory

## Affected
- Maven: `com.typesafe.play:play_2.12` — affected >=0 <2.7.5
- Maven: `com.typesafe.play:play_2.12` — affected >=2.8.0 <2.8.2

## Details
In Play Framework 2.6.0 through 2.8.1, the CSRF filter can be bypassed by making CORS simple requests with content types that contain parameters that can't be parsed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-12480
- https://github.com/playframework/playframework/pull/10285
- https://github.com/playframework/playframework/commit/c82de44fc50b7c58c6e0580f1f67ff08aa7bd154
- https://github.com/playframework/playframework
- https://www.playframework.com/security/vulnerability
- https://www.playframework.com/security/vulnerability/CVE-2020-12480-CsrfBlacklistBypass
