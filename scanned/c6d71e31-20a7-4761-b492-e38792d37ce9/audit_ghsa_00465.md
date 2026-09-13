# [H] Spring Framework when used in combination with any versions of Spring Security contains an authorization bypass

## Summary
Severity: High
Advisory: GHSA-cxrj-66c5-9fmh
CVE: CVE-2018-1258
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-cxrj-66c5-9fmh
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-core` — affected >=5.0.5.RELEASE <5.0.6.RELEASE

## Details
Spring Framework version 5.0.5 when used in combination with any versions of Spring Security contains an authorization bypass when using method security. An unauthorized malicious user can gain unauthorized access to methods that should be restricted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1258
- https://github.com/spring-projects/spring-framework/commit/7b8fa90d96aaf751a3256fa755d5f17e081c20f1
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://web.archive.org/web/20200807033751/http://www.securitytracker.com/id/1041896
- https://web.archive.org/web/20200807025819/http://www.securitytracker.com/id/1041888
- https://web.archive.org/web/20200227032934/http://www.securityfocus.com/bid/104222
- https://security.netapp.com/advisory/ntap-20181018-0002
- https://pivotal.io/security/cve-2018-1258
- https://github.com/spring-projects/spring-framework
- https://github.com/advisories/GHSA-cxrj-66c5-9fmh
- https://access.redhat.com/errata/RHSA-2019:2413
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
