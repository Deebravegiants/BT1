# [H] SQL injection in hibernate-core

## Summary
Severity: High
Advisory: GHSA-j8jw-g6fq-mp7h
CVE: CVE-2020-25638
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-j8jw-g6fq-mp7h
Type: github-advisory

## Affected
- Maven: `org.hibernate:hibernate-core` — affected >=5.4.0.Final <5.4.24.Final
- Maven: `org.hibernate:hibernate-core` — affected >=0 <5.3.20.Final

## Details
A flaw was found in hibernate-core in versions prior to 5.3.20.Final and in 5.4.0.Final up to and including 5.4.23.Final. A SQL injection in the implementation of the JPA Criteria API can permit unsanitized literals when a literal is used in the SQL comments of the query. This flaw could allow an attacker to access unauthorized information or possibly conduct further attacks. The highest threat from this vulnerability is to data confidentiality and integrity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25638
- https://github.com/hibernate/hibernate-orm/commit/36ebf7d3836e83e99f2a91777b5389e1daf1f2b7
- https://github.com/hibernate/hibernate-orm/commit/59fede7acaaa1579b561407aefa582311f7ebe78
- https://github.com/hibernate/hibernate-orm/commit/d22bbb5c339c9df7712c3365bb1df97c91b35ec5
- https://bugzilla.redhat.com/show_bug.cgi?id=1881353
- https://github.com/hibernate/hibernate-orm
- https://lists.apache.org/thread.html/r833c1276e41334fa675848a08daf0c61f39009f9f9a400d9f7006d44@%3Cdev.turbine.apache.org%3E
- https://lists.apache.org/thread.html/rf2378209c676a28b71f9b604a3b3517c448540b85367160e558ef9df@%3Ccommits.turbine.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/01/msg00000.html
- https://www.debian.org/security/2021/dsa-4908
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
