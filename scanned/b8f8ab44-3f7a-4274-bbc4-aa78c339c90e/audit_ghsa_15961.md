# [M] Spring Framework DataBinder Case Sensitive Match Exception

## Summary
Severity: Medium
Advisory: GHSA-4gc7-5j7h-4qph
CVE: CVE-2024-38820
CWE: CWE-178
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-10-18
Source: https://github.com/advisories/GHSA-4gc7-5j7h-4qph
Type: github-advisory

## Affected
- Maven: `org.springframework:spring-context` — affected >=6.1.0 <6.1.14
- Maven: `org.springframework:spring-web` — affected >=6.1.0 <6.1.14
- Maven: `org.springframework:spring-web` — affected >=6.0.0
- Maven: `org.springframework:spring-context` — affected >=6.0.0
- Maven: `org.springframework:spring-context` — affected >=0
- Maven: `org.springframework:spring-web` — affected >=0

## Details
The fix for CVE-2022-22968 made disallowedFields patterns in DataBinder case insensitive. However, String.toLowerCase() has some Locale dependent exceptions that could potentially result in fields not protected as expected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38820
- https://github.com/spring-projects/spring-framework/commit/23656aebc6c7d0f9faff1080981eb4d55eff296c
- https://github.com/spring-projects/spring-framework
- https://github.com/spring-projects/spring-framework/commits/v6.2.0-RC2
- https://security.netapp.com/advisory/ntap-20241129-0003
- https://spring.io/security/cve-2024-38820
