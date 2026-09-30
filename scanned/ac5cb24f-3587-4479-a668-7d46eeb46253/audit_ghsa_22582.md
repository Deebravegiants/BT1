# [H] Improper Authentication in Pivotal Spring-LDAP

## Summary
Severity: High
Advisory: GHSA-pjqh-2jcc-5j84
CVE: CVE-2017-8028
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-pjqh-2jcc-5j84
Type: github-advisory

## Affected
- Maven: `org.springframework.ldap:spring-ldap-core` — affected >=1.3.0 <2.3.2

## Details
In Pivotal Spring-LDAP versions 1.3.0 - 2.3.1, when connected to some LDAP servers, when no additional attributes are bound, and when using LDAP BindAuthenticator with org.springframework.ldap.core.support.DefaultTlsDirContextAuthenticationStrategy as the authentication strategy, and setting userSearch, authentication is allowed with an arbitrary password when the username is correct. This occurs because some LDAP vendors require an explicit operation for the LDAP bind to take effect.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-8028
- https://github.com/spring-projects/spring-ldap/commit/08e8ae289bbd1b581986c7238604a147119c1336
- https://access.redhat.com/errata/RHSA-2018:0319
- https://github.com/spring-projects/spring-ldap
- https://lists.debian.org/debian-lts-announce/2017/11/msg00026.html
- https://pivotal.io/security/cve-2017-8028
- https://www.debian.org/security/2017/dsa-4046
- https://www.oracle.com/security-alerts/cpujan2021.html
