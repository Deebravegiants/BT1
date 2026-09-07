# [M] Spring Framework Cross Site Tracing (XST)

## Summary
Severity: Medium
Advisory: GHSA-9gcm-f4x3-8jpw
CVE: CVE-2018-11039
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-9gcm-f4x3-8jpw
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-web` — affected >=5.0.0 <5.0.7
- Maven: `org.springframework:spring-web` — affected >=4.3.0 <4.3.18

## Details
Spring Framework (versions 5.0.x prior to 5.0.7, versions 4.3.x prior to 4.3.18, and older unsupported versions) allow web applications to change the HTTP request method to any HTTP method (including TRACE) using the HiddenHttpMethodFilter in Spring MVC. If an application has a pre-existing XSS vulnerability, a malicious user (or attacker) can use this filter to escalate to an XST (Cross Site Tracing) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11039
- https://github.com/spring-projects/spring-framework/issues/21376
- https://github.com/spring-projects/spring-framework/commit/323ccf99e575343f63d56e229c25c35c170b7ec1
- https://github.com/spring-projects/spring-framework/commit/a5cd01a4c857aaaba7ccc51545fc73dd25b5cba5
- https://github.com/spring-projects/spring-framework/commit/dac97f1b7dac3e70ff603fb6fc9f205b95dd6b01
- https://github.com/spring-projects/spring-framework/commit/f2694a8ed93f1f63f87ce45d0bb638478b426acd
- https://github.com/spring-projects/spring-framework/commit/f64fa3dea10af125d612d3a997aece93d21bc875
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://spring.io/security/cve-2018-11039
- https://pivotal.io/security/cve-2018-11039
- https://lists.debian.org/debian-lts-announce/2021/04/msg00022.html
- https://github.com/spring-projects/spring-framework
- https://github.com/advisories/GHSA-9gcm-f4x3-8jpw
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- http://www.securityfocus.com/bid/107984
