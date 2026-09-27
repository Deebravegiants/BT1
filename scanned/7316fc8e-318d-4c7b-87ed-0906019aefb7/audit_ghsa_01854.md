# [H] Improper Restriction of XML External Entity Reference in com.h2database:h2.

## Summary
Severity: High
Advisory: GHSA-7rpj-hg47-cx62
CVE: CVE-2021-23463
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2021-12-16
Source: https://github.com/advisories/GHSA-7rpj-hg47-cx62
Type: github-advisory

## Affected
- Maven: `com.h2database:h2` — affected >=1.4.198 <2.0.202

## Details
H2 is an embeddable RDBMS written in Java. The package com.h2database:h2 from 1.4.198 and before 2.0.202 are vulnerable to XML External Entity (XXE) Injection via the org.h2.jdbc.JdbcSQLXML class object, when it receives parsed string data from org.h2.jdbc.JdbcResultSet.getSQLXML() method. If it executes the getSource() method when the parameter is DOMSource.class it will trigger the vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23463
- https://github.com/h2database/h2database/issues/3195
- https://github.com/h2database/h2database/pull/3199
- https://github.com/h2database/h2database/pull/3199#issuecomment-1002830390
- https://github.com/boris-unckel/h2database/commit/f9ad6aef2bfa59eba2b4d3e7c4c32d2cce8e8b05
- https://github.com/h2database/h2database/commit/d83285fd2e48fb075780ee95badee6f5a15ea7f8%23diff-008c2e4462609982199cd83e7cf6f1d6b41296b516783f6752c44b9f15dc7bc3
- https://github.com/h2database/h2database
- https://security.netapp.com/advisory/ntap-20230818-0010
- https://snyk.io/vuln/SNYK-JAVA-COMH2DATABASE-1769238
- https://www.oracle.com/security-alerts/cpuapr2022.html
