# [C] Spring Data Commons remote code injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-4fq3-mr56-cg6r
CVE: CVE-2018-1273
CWE: CWE-20, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-4fq3-mr56-cg6r
Type: github-advisory

## Affected
- Maven: `org.springframework.data:spring-data-commons` — affected >=1.13.0 <1.13.11
- Maven: `org.springframework.data:spring-data-commons` — affected >=2.0.0 <2.0.6

## Details
Spring Data Commons, versions prior to 1.13 to 1.13.10, 2.0 to 2.0.5, and older unsupported versions, contain a property binder vulnerability caused by improper neutralization of special elements. An unauthenticated remote malicious user (or attacker) can supply specially crafted request parameters against Spring Data REST backed HTTP resources or using Spring Data's projection-based request payload binding that can lead to a remote code execution attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1273
- https://github.com/spring-projects/spring-data-commons/issues/1721
- https://github.com/spring-projects/spring-data-commons/commit/ae1dd2741ce06d44a0966ecbd6f47beabde2b653
- https://github.com/spring-projects/spring-data-commons/commit/b1a20ae1e82a63f99b3afc6f2aaedb3bf4dc432a
- https://github.com/advisories/GHSA-4fq3-mr56-cg6r
- https://github.com/spring-projects/spring-data-commons
- https://pivotal.io/security/cve-2018-1273
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://mail-archives.apache.org/mod_mbox/ignite-dev/201807.mbox/%3CCAK0qHnqzfzmCDFFi6c5Jok19zNkVCz5Xb4sU%3D0f2J_1i4p46zQ%40mail.gmail.com%3E
