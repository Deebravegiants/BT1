# [M] Keycloak-services: keycloak-services: information disclosure via role-users endpoint bypasses per-user view filter

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-17059
Aliases: CVE-2026-17059
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-17059
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.3

## Details
A flaw was found in the role-users endpoint of the keycloak-services library, which is the core component of the Keycloak identity and access management solution. The issue occurs because the system fails to check if an administrator has permission to view individual users when listing members of a role. This allows a restricted administrator to see private information, such as names and email addresses, for users they should not be able to access.

## References
- https://access.redhat.com/security/cve/CVE-2026-17059
- https://bugzilla.redhat.com/show_bug.cgi?id=2506746
- https://nvd.nist.gov/vuln/detail/CVE-2026-17059
