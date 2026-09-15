# [H] Pivotal Spring Framework Paths provided to the ResourceServlet were not properly sanitized

## Summary
Severity: High
Advisory: GHSA-2m8h-fgr8-2q9w
CVE: CVE-2016-9878
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-04
Source: https://github.com/advisories/GHSA-2m8h-fgr8-2q9w
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-webmvc` — affected >=0 <3.2.18
- Maven: `org.springframework:spring-webmvc` — affected >=4.2.0 <4.2.9
- Maven: `org.springframework:spring-webmvc` — affected >=4.3.0 <4.3.5

## Details
An issue was discovered in Pivotal Spring Framework before 3.2.18, 4.2.x before 4.2.9, and 4.3.x before 4.3.5. Paths provided to the ResourceServlet were not properly sanitized and as a result exposed to directory traversal attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9878
- https://github.com/spring-projects/spring-framework/issues/19513
- https://github.com/spring-projects/spring-framework/commit/43bf008fbcd0d7945e2fcd5e30039bc4d74c7a98
- https://github.com/spring-projects/spring-framework/commit/a7dc48534ea501525f11369d369178a60c2f47d0
- https://github.com/spring-projects/spring-framework/commit/e2d6e709c3c65a4951eb096843ee75d5200cfcad
- https://access.redhat.com/errata/RHSA-2017:3115
- https://github.com/advisories/GHSA-2m8h-fgr8-2q9w
- https://github.com/spring-projects/spring-framework
- https://lists.debian.org/debian-lts-announce/2019/07/msg00012.html
- https://pivotal.io/security/cve-2016-9878
- https://security.netapp.com/advisory/ntap-20180419-0002
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- http://www.oracle.com/technetwork/security-advisory/cpuapr2018-3678067.html
- http://www.oracle.com/technetwork/security-advisory/cpujan2018-3236628.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.securityfocus.com/bid/95072
- http://www.securitytracker.com/id/1040698
