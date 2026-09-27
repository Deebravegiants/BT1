# [M] Keycloak: Missing Role Enforcement on UMA 2.0 Permission Ticket Endpoint Leads to Information Disclosure

## Summary
Severity: Medium
Advisory: GHSA-q35r-vvhv-vx5h
CVE: CVE-2026-3190
CWE: CWE-280
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-q35r-vvhv-vx5h
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-server-spi-private` — affected >=0 <26.5.6
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.5.6
- Maven: `org.keycloak:keycloak-model-jpa` — affected >=0 <26.5.6

## Details
A flaw was found in Keycloak. The User-Managed Access (UMA) 2.0 Protection API endpoint for permission tickets fails to enforce the `uma_protection` role check. This allows any authenticated user with a token issued for a resource server client, even without the `uma_protection` role, to enumerate all permission tickets in the system. This vulnerability partial leads to information disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3190
- https://github.com/keycloak/keycloak/issues/46723
- https://github.com/keycloak/keycloak/commit/f1baf25cbb1551202570f954102eb2d270ab0694
- https://access.redhat.com/errata/RHSA-2026:6477
- https://access.redhat.com/errata/RHSA-2026:6478
- https://access.redhat.com/security/cve/CVE-2026-3190
- https://bugzilla.redhat.com/show_bug.cgi?id=2442572
- https://github.com/keycloak/keycloak
