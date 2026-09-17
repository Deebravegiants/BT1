# [M] Keycloak-services: keycloak-services: vault-resolved rotated client secrets leaked via admin rest api

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-17048
Aliases: CVE-2026-17048
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-17048
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.2

## Details
A flaw was found in the Keycloak Admin REST API, which is used to manage security realms and clients. The issue occurs when the system processes requests for rotated client secrets that are stored in a secure vault. Due to improper boundary enforcement, a delegated administrator with view-only permissions can retrieve the actual resolved secret instead of the vault placeholder, leading to the exposure of sensitive credentials.

## References
- https://access.redhat.com/errata/RHSA-2026:56523
- https://access.redhat.com/errata/RHSA-2026:56524
- https://access.redhat.com/security/cve/CVE-2026-17048
- https://bugzilla.redhat.com/show_bug.cgi?id=2506743
- https://nvd.nist.gov/vuln/detail/CVE-2026-17048
