# [M] Spring Security logout not clearing security context

## Summary
Severity: Medium
Advisory: GHSA-x873-6rgc-94jc
CVE: CVE-2023-20862
CWE: CWE-459
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-04-19
Source: https://github.com/advisories/GHSA-x873-6rgc-94jc
Type: github-advisory

## Affected
- Maven: `org.springframework.security:spring-security-core` — affected >=5.7.0 <5.7.8
- Maven: `org.springframework.security:spring-security-core` — affected >=5.8.0 <5.8.3
- Maven: `org.springframework.security:spring-security-core` — affected >=6.0.0 <6.0.3

## Details
In Spring Security, versions 5.7.x prior to 5.7.8, versions 5.8.x prior to 5.8.3, and versions 6.0.x prior to 6.0.3, the logout support does not properly clean the security context if using serialized versions. Additionally, it is not possible to explicitly save an empty security context to the HttpSessionSecurityContextRepository. This vulnerability can keep users authenticated even after they performed logout. Users of affected versions should apply the following mitigation. 5.7.x users should upgrade to 5.7.8. 5.8.x users should upgrade to 5.8.3. 6.0.x users should upgrade to 6.0.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-20862
- https://github.com/spring-projects/spring-security
- https://security.netapp.com/advisory/ntap-20230526-0002
- https://spring.io/security/cve-2023-20862
