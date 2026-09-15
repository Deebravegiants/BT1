# [H] org.keycloak:keycloak-services has Inefficient Regular Expression Complexity

## Summary
Severity: High
Advisory: GHSA-wq8x-cg39-8mrr
CVE: CVE-2024-10270
CWE: CWE-1333
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-11-25
Source: https://github.com/advisories/GHSA-wq8x-cg39-8mrr
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <24.0.9
- Maven: `org.keycloak:keycloak-services` — affected >=25.0.0 <26.0.6

## Details
A vulnerability was found in the Keycloak-services package. If untrusted data is passed to the SearchQueryUtils method, it could lead to a denial of service (DoS) scenario by exhausting system resources due to a Regex complexity.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-wq8x-cg39-8mrr
- https://nvd.nist.gov/vuln/detail/CVE-2024-10270
- https://github.com/keycloak/keycloak/commit/5d6c91f3309db468b0fe4834e88c3d25649f73e4
- https://access.redhat.com/errata/RHSA-2024:10175
- https://access.redhat.com/errata/RHSA-2024:10176
- https://access.redhat.com/errata/RHSA-2024:10177
- https://access.redhat.com/errata/RHSA-2024:10178
- https://access.redhat.com/security/cve/CVE-2024-10270
- https://bugzilla.redhat.com/show_bug.cgi?id=2321214
- https://github.com/keycloak/keycloak
