# [M] Keycloak-services: keycloak-services: client access-type policy condition bypass during client update

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-18573
Aliases: CVE-2026-18573
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-18573
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.3

## Details
A flaw was found in the keycloak-services component of Keycloak, which is used for managing authentication and authorization flows. The issue occurs when a realm administrator configures client policies to enforce specific authentication requirements on confidential clients. Due to improper evaluation of the client state during an update operation, an attacker with client management permissions can bypass these security policies by first creating a public client and then updating it to a confidential client with weaker authentication. This can result in the persistence of clients that do not comply with the intended security hardening of the realm.

## References
- https://access.redhat.com/security/cve/CVE-2026-18573
- https://bugzilla.redhat.com/show_bug.cgi?id=2509764
- https://nvd.nist.gov/vuln/detail/CVE-2026-18573
