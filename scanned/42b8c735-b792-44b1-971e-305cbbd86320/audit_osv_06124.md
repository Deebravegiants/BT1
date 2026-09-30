# [H] Keycloak-services: keycloak-services: default dcr policy allows role forgery via user property mappers

## Summary
Severity: High
Advisory: BIT-keycloak-2026-16102
Aliases: CVE-2026-16102
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-16102
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=26.6.0 <26.6.5

## Details
A flaw was found in the Dynamic Client Registration (DCR) component of Keycloak, an identity and access management solution. The default DCR policy fails to properly validate the claim path for User Property mappers, allowing them to write values to sensitive internal claim locations. An attacker with a standard user account and a limited Initial Access Token can exploit this to forge administrative roles in their access token. This allows the attacker to take over other clients, steal confidential secrets, and potentially gain full administrative control over the realm.

## References
- https://access.redhat.com/errata/RHSA-2026:50846
- https://access.redhat.com/errata/RHSA-2026:50847
- https://access.redhat.com/errata/RHSA-2026:50848
- https://access.redhat.com/errata/RHSA-2026:50849
- https://access.redhat.com/security/cve/CVE-2026-16102
- https://bugzilla.redhat.com/show_bug.cgi?id=2501735
- https://nvd.nist.gov/vuln/detail/CVE-2026-16102
