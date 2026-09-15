# [C] Authorization bypass in Spring Security

## Summary
Severity: Critical
Advisory: GHSA-hh32-7344-cg2f
CVE: CVE-2022-22978
CWE: CWE-285, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-20
Source: https://github.com/advisories/GHSA-hh32-7344-cg2f
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=5.5.0 <5.5.7
- Maven: `org.springframework.security:spring-security-core` — affected >=5.6.0 <5.6.4
- Maven: `org.springframework.security:spring-security-core` — affected >=0 <5.4.11
- Maven: `org.springframework.security:spring-security-web` — affected >=5.5.0 <5.5.7
- Maven: `org.springframework.security:spring-security-web` — affected >=5.6.0 <5.6.4
- Maven: `org.springframework.security:spring-security-web` — affected >=0 <5.4.11

## Details
In Spring Security versions 5.5.6 and 5.5.7 and older unsupported versions, RegexRequestMatcher can easily be misconfigured to be bypassed on some servlet containers. Applications using RegexRequestMatcher with `.` in the regular expression are possibly vulnerable to an authorization bypass.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22978
- https://github.com/anchore/grype/issues/2158
- https://github.com/spring-projects/spring-security
- https://github.com/spring-projects/spring-security/blob/main/web/src/main/java/org/springframework/security/web/util/matcher/RegexRequestMatcher.java
- https://security.netapp.com/advisory/ntap-20220707-0003
- https://spring.io/security/cve-2022-22978
- https://tanzu.vmware.com/security/cve-2022-22978
- https://www.oracle.com/security-alerts/cpujul2022.html
