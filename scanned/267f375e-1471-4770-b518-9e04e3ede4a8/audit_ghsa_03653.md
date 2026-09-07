# [H] Insufficiently Protected Credentials and Improper Authentication in Spring Security

## Summary
Severity: High
Advisory: GHSA-v33x-prhc-gph5
CVE: CVE-2019-11272
CWE: CWE-287, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2019-06-27
Source: https://github.com/advisories/GHSA-v33x-prhc-gph5
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=0 <4.2.13
- Maven: `org.springframework.security:spring-security-cas` — affected >=0 <4.2.13.RELEASE

## Details
Spring Security, versions 4.2.x up to 4.2.12, and older unsupported versions support plain text passwords using PlaintextPasswordEncoder. If an application using an affected version of Spring Security is leveraging PlaintextPasswordEncoder and a user has a null encoded password, a malicious user (or attacker) can authenticate using a password of ?null?.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11272
- https://lists.debian.org/debian-lts-announce/2019/07/msg00008.html
- https://pivotal.io/security/cve-2019-11272
