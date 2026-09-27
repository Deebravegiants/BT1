# [M] Improper Control of Generation of Code in Spring Security

## Summary
Severity: Medium
Advisory: GHSA-5xm9-rf63-wj7h
CVE: CVE-2011-2732
CWE: CWE-94
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5xm9-rf63-wj7h
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=0 <2.0.7
- Maven: `org.springframework.security:spring-security-core` — affected >=3.0.0 <3.0.6

## Details
CRLF injection vulnerability in the logout functionality in VMware SpringSource Spring Security before 2.0.7 and 3.0.x before 3.0.6 allows remote attackers to inject arbitrary HTTP headers and conduct HTTP response splitting attacks via the spring-security-redirect parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-2732
- https://github.com/spring-projects/spring-security
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=677814
- http://support.springsource.com/security/cve-2011-2732
