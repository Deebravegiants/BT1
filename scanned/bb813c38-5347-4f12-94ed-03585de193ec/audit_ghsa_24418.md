# [M] Exposure of Sensitive Information to an Unauthorized Actor in Spring Security

## Summary
Severity: Medium
Advisory: GHSA-3533-rvpc-6x56
CVE: CVE-2012-5055
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-3533-rvpc-6x56
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=0 <2.0.8
- Maven: `org.springframework.security:spring-security-core` — affected >=3.0.0 <3.0.8
- Maven: `org.springframework.security:spring-security-core` — affected >=3.1.0 <3.1.3

## Details
DaoAuthenticationProvider in VMware SpringSource Spring Security before 2.0.8, 3.0.x before 3.0.8, and 3.1.x before 3.1.3 does not check the password if the user is not found, which makes the response delay shorter and might allow remote attackers to enumerate valid usernames via a series of login requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-5055
- http://support.springsource.com/security/CVE-2012-5055
