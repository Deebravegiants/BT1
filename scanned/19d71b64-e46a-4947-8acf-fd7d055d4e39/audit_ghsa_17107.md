# [H] Erroneous authentication pass in Spring Security

## Summary
Severity: High
Advisory: GHSA-f3jh-qvm4-mg39
CVE: CVE-2024-22257
CWE: CWE-287, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-03-18
Source: https://github.com/advisories/GHSA-f3jh-qvm4-mg39
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=0 <5.7.12
- Maven: `org.springframework.security:spring-security-core` — affected >=5.8.0 <5.8.11
- Maven: `org.springframework.security:spring-security-core` — affected >=6.0.0 <6.1.8
- Maven: `org.springframework.security:spring-security-core` — affected >=6.2.0 <6.2.3

## Details
In Spring Security, versions 5.7.x prior to 5.7.12, 5.8.x prior to 5.8.11, versions 6.0.x prior to 6.0.9, versions 6.1.x prior to 6.1.8, versions 6.2.x prior to 6.2.3, an application is possible vulnerable to broken access control when it directly uses the AuthenticatedVoter#vote passing a null Authentication parameter.

Specifically, an application is vulnerable if:

The application uses AuthenticatedVoter directly and a null authentication parameter is passed to it resulting in an erroneous true return value.

An application is not vulnerable if any of the following is true:

* The application does not use AuthenticatedVoter#vote directly.
* The application does not pass null to AuthenticatedVoter#vote.

Note that AuthenticatedVoter is deprecated since 5.8, use implementations of AuthorizationManager as a replacement.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22257
- https://github.com/spring-projects/spring-security/commit/5a7f12f1a9fdb4edaab6f61495f1d781a7273b61
- https://github.com/spring-projects/spring-security
- https://security.netapp.com/advisory/ntap-20240419-0005
- https://spring.io/security/cve-2024-22257
