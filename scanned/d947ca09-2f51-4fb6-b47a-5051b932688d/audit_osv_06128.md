# [M] Keycloak-services: keycloak-services: realm default-group reads disclose hidden groups under fgap v2

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-16108
Aliases: CVE-2026-16108
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-16108
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.3

## Details
A flaw was found in the default-groups REST endpoint and realm representation of Keycloak. This component is responsible for managing groups that are automatically assigned to new users within a realm. The issue allows a delegated administrator with realm-viewing permissions to see the names and identifiers of hidden default groups, even if they lack the specific permissions to view those groups. This can lead to the exposure of sensitive organizational structures or internal group names.

## References
- https://access.redhat.com/security/cve/CVE-2026-16108
- https://bugzilla.redhat.com/show_bug.cgi?id=2501740
- https://nvd.nist.gov/vuln/detail/CVE-2026-16108
