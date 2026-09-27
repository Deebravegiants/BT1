# [M] SQL Injection in Hibernate ORM

## Summary
Severity: Medium
Advisory: GHSA-8grg-q944-cch5
CVE: CVE-2019-14900
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-8grg-q944-cch5
Type: github-advisory

## Affected
- Maven: `org.hibernate:hibernate-core` — affected >=0 <5.3.18
- Maven: `org.hibernate:hibernate-core` — affected >=5.4.0 <5.4.18
- Maven: `org.hibernate:hibernate-core` — affected >=5.5.0.Alpha1 <5.5.0.Beta1

## Details
A flaw was found in Hibernate ORM in versions before 5.3.18, 5.4.18 and 5.5.0.Beta1. A SQL injection in the implementation of the JPA Criteria API can permit unsanitized literals when a literal is used in the SELECT or GROUP BY parts of the query. This flaw could allow an attacker to access unauthorized information or possibly conduct further attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14900
- https://github.com/hibernate/hibernate-orm/commit/3f3c1ab50604ab9ba99e25d2016fb85f3ba9dcd4
- https://github.com/hibernate/hibernate-orm/commit/646b383f959eff18d58081b1a574f0d777d353da
- https://github.com/hibernate/hibernate-orm/commit/e0e22ea256c1906235d6a8e90b79c4ce33d0861f
- https://github.com/hibernate/hibernate-orm/commit/eebf01fbf3c2550ee70cdc9c1b02b52e330c8c36
- https://bugzilla.redhat.com/show_bug.cgi?id=1666499
- https://github.com/hibernate/hibernate-orm
- https://lists.apache.org/thread.html/r833c1276e41334fa675848a08daf0c61f39009f9f9a400d9f7006d44@%3Cdev.turbine.apache.org%3E
- https://security.netapp.com/advisory/ntap-20220210-0020
