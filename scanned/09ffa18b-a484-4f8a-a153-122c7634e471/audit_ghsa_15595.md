# [H] Keycloak Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-w97f-w3hq-36g2
CVE: CVE-2023-6841
CWE: CWE-231
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-09-10
Source: https://github.com/advisories/GHSA-w97f-w3hq-36g2
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <24.0.0

## Details
A denial of service vulnerability was found in keycloak where the amount of attributes per object is not limited, an attacker by sending repeated HTTP requests could cause a resource exhaustion when the application send back rows with long attribute values. The issue is fixed in Keycloak 24 with the introduction of the User Profile feature.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6841
- https://github.com/keycloak/keycloak/issues/32837
- https://access.redhat.com/security/cve/CVE-2023-6841
- https://bugzilla.redhat.com/show_bug.cgi?id=2254714
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/releases/tag/24.0.0
