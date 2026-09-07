# [M] Spoofing attack in swagger-ui

## Summary
Severity: Medium
Advisory: GHSA-cr3q-pqgq-m8c2
CVE: CVE-2018-25031
CWE: CWE-20, CWE-918, CWE-922
Ecosystem: Maven, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-03-12
Source: https://github.com/advisories/GHSA-cr3q-pqgq-m8c2
Type: github-advisory

## Affected
- npm: `swagger-ui` — affected >=0 <4.1.3
- Maven: `org.webjars:swagger-ui` — affected >=0 <4.1.3

## Details
Swagger UI before 4.1.3 could allow a remote attacker to conduct spoofing attacks. By persuading a victim to open a crafted URL, an attacker could exploit this vulnerability to display remote OpenAPI definitions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25031
- https://github.com/swagger-api/swagger-ui/issues/4872
- https://github.com/swagger-api/swagger-ui/pull/7697
- https://github.com/swagger-api/swagger-ui
- https://github.com/swagger-api/swagger-ui/releases/tag/v4.1.3
- https://security.netapp.com/advisory/ntap-20220407-0004
- https://security.snyk.io/vuln/SNYK-JS-SWAGGERUI-2314885
