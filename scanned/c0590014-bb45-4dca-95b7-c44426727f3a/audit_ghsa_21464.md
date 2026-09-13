# [C] Spring Security authorization rules can be bypassed via forward or include dispatcher types

## Summary
Severity: Critical
Advisory: GHSA-mmmh-wcxm-2wr4
CVE: CVE-2022-31692
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-01
Source: https://github.com/advisories/GHSA-mmmh-wcxm-2wr4
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=5.7.0 <5.7.5
- Maven: `org.springframework.security:spring-security-core` — affected >=5.6.0 <5.6.9

## Details
Spring Security, versions 5.7 prior to 5.7.5 and 5.6 prior to 5.6.9 could be susceptible to authorization rules bypass via forward or include dispatcher types. Specifically, an application is vulnerable when all of the following are true: The application expects that Spring Security applies security to forward and include dispatcher types. The application uses the AuthorizationFilter either manually or via the authorizeHttpRequests() method. The application configures the FilterChainProxy to apply to forward and/or include requests (e.g. spring.security.filter.dispatcher-types = request, error, async, forward, include). The application may forward or include the request to a higher privilege-secured endpoint.The application configures Spring Security to apply to every dispatcher type via authorizeHttpRequests().shouldFilterAllDispatcherTypes(true)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-31692
- https://github.com/spring-projects/spring-security
- https://security.netapp.com/advisory/ntap-20221215-0010
- https://tanzu.vmware.com/security/cve-2022-31692
