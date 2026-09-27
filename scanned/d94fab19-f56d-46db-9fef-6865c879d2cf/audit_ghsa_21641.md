# [H] Out-of-bounds Write in Play Framework

## Summary
Severity: High
Advisory: GHSA-h48w-c35p-6m8x
CVE: CVE-2020-27196
CWE: CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-h48w-c35p-6m8x
Type: github-advisory

## Affected
- Maven: `com.typesafe.play:play` — affected >=2.6.0 <2.7.6
- Maven: `com.typesafe.play:play` — affected >=2.8.0 <2.8.3
- Maven: `com.typesafe.play:play-java` — affected >=2.6.0 <2.7.6
- Maven: `com.typesafe.play:play-java` — affected >=2.8.0 <2.8.3

## Details
An issue was discovered in PlayJava in Play Framework 2.6.0 through 2.8.2. The body parsing of HTTP requests eagerly parses a payload given a Content-Type header. A deep JSON structure sent to a valid POST endpoint (that may or may not expect JSON payloads) causes a StackOverflowError and Denial of Service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-27196
- https://github.com/playframework/playframework/pull/10321
- https://www.playframework.com/security/vulnerability/CVE-2020-27196-DosViaJsonStackOverflow
