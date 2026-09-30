# [M] Keycloak: keycloak: unauthorized access to resources via uma permission ticket bypass

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-9799
Aliases: CVE-2026-9799
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-9799
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=26.6.0 <26.6.4

## Details
A flaw was found in org.keycloak.authorization. An authenticated user with a granted User-Managed Access (UMA) permission ticket for one resource can exploit this by using a specific permission request prefix to bypass per-resource access control. This allows the user to gain unauthorized access to all resources of that type within the same resource server, even if they do not have a ticket for those specific resources. This vulnerability requires the resource server to be configured in PERMISSIVE policy enforcement mode and affects typed resources with ownerManagedAccess enabled, where no explicit policy protects the resource type. The primary consequence is unauthorized information disclosure or modification of resources.

## References
- https://access.redhat.com/errata/RHSA-2026:30049
- https://access.redhat.com/errata/RHSA-2026:30050
- https://access.redhat.com/errata/RHSA-2026:30083
- https://access.redhat.com/errata/RHSA-2026:30084
- https://access.redhat.com/security/cve/CVE-2026-9799
- https://bugzilla.redhat.com/show_bug.cgi?id=2482471
- https://nvd.nist.gov/vuln/detail/CVE-2026-9799
