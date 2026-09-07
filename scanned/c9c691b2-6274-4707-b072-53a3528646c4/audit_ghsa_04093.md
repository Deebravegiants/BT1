# [M] Spring Security uses insufficiently random values

## Summary
Severity: Medium
Advisory: GHSA-v2r2-7qm7-jj6v
CVE: CVE-2019-3795
CWE: CWE-330
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-04-16
Source: https://github.com/advisories/GHSA-v2r2-7qm7-jj6v
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=4.2.0 <4.2.12
- Maven: `org.springframework.security:spring-security-core` — affected >=5.0.0 <5.0.12
- Maven: `org.springframework.security:spring-security-core` — affected >=5.1.0 <5.1.5

## Details
Spring Security versions 4.2.x prior to 4.2.12, 5.0.x prior to 5.0.12, and 5.1.x prior to 5.1.5 contain an insecure randomness vulnerability when using SecureRandomFactoryBean#setSeed to configure a SecureRandom instance. In order to be impacted, an honest application must provide a seed and make the resulting random material available to an attacker for inspection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3795
- https://github.com/advisories/GHSA-v2r2-7qm7-jj6v
- https://lists.debian.org/debian-lts-announce/2019/05/msg00026.html
- https://pivotal.io/security/cve-2019-3795
- http://www.securityfocus.com/bid/107802
