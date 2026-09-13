# [M] Spring Vault vulnerable to insertion of sensitive information into a log file

## Summary
Severity: Medium
Advisory: GHSA-r47r-87p9-8jh3
CVE: CVE-2023-20859
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-23
Source: https://github.com/advisories/GHSA-r47r-87p9-8jh3
Type: github-advisory

## Affected
- Maven: `org.springframework.vault:spring-vault-core` — affected >=3.0.0 <3.0.2
- Maven: `org.springframework.vault:spring-vault-core` — affected >=0 <2.3.3

## Details
In Spring Vault, versions 3.0.x prior to 3.0.2 and versions 2.3.x prior to 2.3.3 and older versions, an application is vulnerable to insertion of sensitive information into a log file when it attempts to revoke a Vault batch token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-20859
- https://github.com/spring-projects/spring-vault
- https://spring.io/security/cve-2023-20859
