# [M] CVE-2016-6652

## Summary
Severity: Medium
Advisory: CVE-2016-6652
Aliases: GHSA-xr4v-28rm-pvgw
CVSS: 5.6 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2016-10-05
Source: https://osv.dev/vulnerability/CVE-2016-6652
Type: osv

## Details
SQL injection vulnerability in Pivotal Spring Data JPA before 1.9.6 (Gosling SR6) and 1.10.x before 1.10.4 (Hopper SR4), when used with a repository that defines a String query using the @Query annotation, allows attackers to execute arbitrary JPQL commands via a sort instance with a function call.

## References
- http://www.securityfocus.com/bid/93276
- https://jira.spring.io/browse/DATAJPA-965
- https://pivotal.io/security/cve-2016-6652
- https://security.gentoo.org/glsa/201701-01
- https://github.com/spring-projects/spring-data-jpa/commit/b8e7fe
