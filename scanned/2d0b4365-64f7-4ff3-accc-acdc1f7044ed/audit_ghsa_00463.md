# [H] Improper Restriction of Operations within the Bounds of a Memory Buffer in akka-http-core

## Summary
Severity: High
Advisory: GHSA-gfx6-ph4q-q54q
CVE: CVE-2017-1000118
CWE: CWE-119
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-22
Source: https://github.com/advisories/GHSA-gfx6-ph4q-q54q
Type: github-advisory

## Affected
- Maven: `com.typesafe.akka:akka-http-core_2.12` — affected >=0 <10.0.6
- Maven: `com.typesafe.akka:akka-http-core_2.11` — affected >=0 <10.0.6

## Details
Akka HTTP versions <= 10.0.5 Illegal Media Range in Accept Header Causes StackOverflowError Leading to Denial of Service

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000118
- https://doc.akka.io/docs/akka-http/10.0.6/security/2017-05-03-illegal-media-range-in-accept-header-causes-stackoverflowerror.html
- https://github.com/advisories/GHSA-gfx6-ph4q-q54q
