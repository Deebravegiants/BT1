# [M] Incorrect Authorization in Spring Cloud Netflix Zuul

## Summary
Severity: Medium
Advisory: GHSA-vwpg-f6gw-rjvf
CVE: CVE-2021-22113
CWE: CWE-863
Ecosystem: Maven
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-vwpg-f6gw-rjvf
Type: github-advisory

## Affected
- Maven: `org.springframework.cloud:spring-cloud-netflix-zuul` — affected >=0 <2.2.7

## Details
Applications using the “Sensitive Headers” functionality in Spring Cloud Netflix Zuul 2.2.6.RELEASE and below may be vulnerable to bypassing the “Sensitive Headers” restriction when executing requests with specially constructed URLs. Applications that use Spring Security's StrictHttpFirewall (enabled by default for all URLs) are not affected by the vulnerability, as they reject requests that allow bypassing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22113
- https://github.com/spring-cloud/spring-cloud-netflix/commit/8ecb3dca511c3ce0454e42ac31ee2331d7318c07
- https://tanzu.vmware.com/security/cve-2021-22113
