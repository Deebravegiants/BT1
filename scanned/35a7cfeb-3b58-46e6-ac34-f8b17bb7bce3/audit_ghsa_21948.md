# [M] Cross-Site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-q42q-523g-3fwv
CVE: CVE-2020-7780
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-q42q-523g-3fwv
Type: github-advisory

## Affected
- Maven: `com.softwaremill.akka-http-session:core_2.13` — affected >=0 <0.5.11
- Maven: `com.softwaremill.akka-http-session:core_2.12` — affected >=0 <0.5.11
- Maven: `com.softwaremill.akka-http-session:core_2.11` — affected >=0 <0.5.11

## Details
This affects the package com.softwaremill.akka-http-session:core_2.13 before 0.5.11; the package com.softwaremill.akka-http-session:core_2.12 before 0.5.11; the package com.softwaremill.akka-http-session:core_2.11 before 0.5.11. For older versions, endpoints protected by randomTokenCsrfProtection could be bypassed with an empty X-XSRF-TOKEN header and an empty XSRF-TOKEN cookie.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7780
- https://github.com/softwaremill/akka-http-session/issues/74
- https://github.com/softwaremill/akka-http-session/issues/77
- https://github.com/softwaremill/akka-http-session/commit/57f11663eecb84be03383d164f655b9c5f953b41
- https://snyk.io/vuln/SNYK-JAVA-COMSOFTWAREMILLAKKAHTTPSESSION-1045352
- https://snyk.io/vuln/SNYK-JAVA-COMSOFTWAREMILLAKKAHTTPSESSION-1046654
- https://snyk.io/vuln/SNYK-JAVA-COMSOFTWAREMILLAKKAHTTPSESSION-1046655
