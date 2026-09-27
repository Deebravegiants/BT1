# [H] Cross-Site Request Forgery in com.softwaremill.akka-http-session:core_2.12

## Summary
Severity: High
Advisory: GHSA-4jf5-jggp-g56j
CVE: CVE-2020-28452
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-4jf5-jggp-g56j
Type: github-advisory

## Affected
- Maven: `com.softwaremill.akka-http-session:core_2.12` — affected >=0.3.0 <0.6.1

## Details
This affects the package com.softwaremill.akka-http-session:core_2.12 from 0 and before 0.6.1; all versions of package com.softwaremill.akka-http-session:core_2.11; the package com.softwaremill.akka-http-session:core_2.13 from 0 and before 0.6.1. CSRF protection can be bypassed by forging a request that contains the same value for both the X-XSRF-TOKEN header and the XSRF-TOKEN cookie value, as the check in randomTokenCsrfProtection only checks that the two values are equal and non-empty.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28452
- https://github.com/softwaremill/akka-http-session/issues/77
- https://github.com/softwaremill/akka-http-session/pull/79
- https://github.com/softwaremill/akka-http-session/commit/8725dccfc3143ac52304a51f4bbfda119d5ba3a1
- https://snyk.io/vuln/SNYK-JAVA-COMSOFTWAREMILLAKKAHTTPSESSION-1046674
- https://snyk.io/vuln/SNYK-JAVA-COMSOFTWAREMILLAKKAHTTPSESSION-1046675
- https://snyk.io/vuln/SNYK-JAVA-COMSOFTWAREMILLAKKAHTTPSESSION-1058933
