# [H] Keycloak affected by improper invitation token validation

## Summary
Severity: High
Advisory: GHSA-hcvw-475w-8g7p
CVE: CVE-2026-1529
CWE: CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-hcvw-475w-8g7p
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=26.5.0 <26.5.3
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.2.13
- Maven: `org.keycloak:keycloak-services` — affected >=26.3.0 <26.4.9

## Details
A flaw was found in Keycloak. An attacker can exploit this vulnerability by modifying the organization ID and target email within a legitimate invitation token's JSON Web Token (JWT) payload. This lack of cryptographic signature verification allows the attacker to successfully self-register into an unauthorized organization, leading to unauthorized access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1529
- https://github.com/keycloak/keycloak/issues/46145
- https://github.com/keycloak/keycloak/pull/46155
- https://github.com/keycloak/keycloak/commit/82cd7941d1dd28fa14a67a6e6b912301f1a5e1a1
- https://github.com/keycloak/keycloak/commit/8fc9a98026106a326f4faa98d4c9a48341ace2d7
- https://github.com/keycloak/keycloak/commit/b2519756487b519f95c07aa8b10afe003e492119
- https://access.redhat.com/errata/RHSA-2026:2363
- https://access.redhat.com/errata/RHSA-2026:2364
- https://access.redhat.com/errata/RHSA-2026:2365
- https://access.redhat.com/errata/RHSA-2026:2366
- https://access.redhat.com/security/cve/CVE-2026-1529
- https://bugzilla.redhat.com/show_bug.cgi?id=2433783
- https://github.com/keycloak/keycloak
