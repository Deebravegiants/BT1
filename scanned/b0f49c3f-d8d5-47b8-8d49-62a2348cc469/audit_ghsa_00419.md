# [H] Spring Security and Spring Framework may not recognize certain paths that should be protected

## Summary
Severity: High
Advisory: GHSA-8crv-49fr-2h6j
CVE: CVE-2016-5007
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-8crv-49fr-2h6j
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-core` — affected >=0 <4.3.1
- Maven: `org.springframework.security:spring-security-core` — affected >=0 <4.1.1

## Details
Both Spring Security 3.2.x, 4.0.x, 4.1.0 and the Spring Framework 3.2.x, 4.0.x, 4.1.x, 4.2.x (as well as other unsupported versions) rely on URL pattern mappings for authorization and for mapping requests to controllers respectively. Differences in the strictness of the pattern matching mechanisms, for example with regards to space trimming in path segments, can lead Spring Security to not recognize certain paths as not protected that are in fact mapped to Spring MVC controllers that should be protected. The problem is compounded by the fact that the Spring Framework provides richer features with regards to pattern matching as well as by the fact that pattern matching in each Spring Security and the Spring Framework can easily be customized creating additional differences.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5007
- https://github.com/spring-projects/spring-security/issues/3964
- https://github.com/spring-projects/spring-framework/commit/a30ab30e4e9ae021fdda04e9abfc228476b846b5
- https://github.com/spring-projects/spring-security/commit/e4c13e3c0ee7f06f59d3b43ca6734215ad7d8974
- https://github.com/advisories/GHSA-8crv-49fr-2h6j
- https://pivotal.io/security/cve-2016-5007
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- http://www.oracle.com/technetwork/security-advisory/cpuapr2018-3678067.html
- http://www.securityfocus.com/bid/91687
