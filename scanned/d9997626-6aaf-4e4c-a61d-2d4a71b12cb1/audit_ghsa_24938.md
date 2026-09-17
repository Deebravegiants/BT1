# [M] Authentication Bypass Using an Alternate Path or Channel in SpringSource Spring Security and Acegi Security

## Summary
Severity: Medium
Advisory: GHSA-3295-h9qx-r82x
CVE: CVE-2010-3700
CWE: CWE-288
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-3295-h9qx-r82x
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=2.0.0 <2.0.6
- Maven: `org.springframework.security:spring-security-core` — affected >=3.0.0 <3.0.4
- Maven: `org.acegisecurity:acegi-security` — affected >=1.0.0

## Details
VMware SpringSource Spring Security 2.x before 2.0.6 and 3.x before 3.0.4, and Acegi Security 1.0.0 through 1.0.7, as used in IBM WebSphere Application Server (WAS) 6.1 and 7.0, allows remote attackers to bypass security constraints via a path parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-3700
- https://issues.apache.org/bugzilla/show_bug.cgi?id=25015
- https://web.archive.org/web/20110802082343/http://www.springsource.com/security/cve-2010-3700
