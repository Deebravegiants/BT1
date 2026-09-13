# [M] Keycloak leaks sensitive information in logged exceptions

## Summary
Severity: Medium
Advisory: GHSA-qgmm-f2qw-r95f
CVE: CVE-2020-1698
CWE: CWE-200, CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qgmm-f2qw-r95f
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <9.0.0

## Details
A flaw was found in keycloak in versions before 9.0.0. A logged exception in the HttpMethod class may leak the password given as parameter. The highest threat from this vulnerability is to data confidentiality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1698
- https://github.com/keycloak/keycloak/pull/6751
- https://github.com/keycloak/keycloak/commit/62c9e1577618470832ede22dcedd46cba15b1836
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1698
