# [M] Keycloak-services: keycloak-services: group hierarchy search discloses hidden parent groups under fgap v2

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-15945
Aliases: CVE-2026-15945
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-15945
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.2

## Details
A flaw was found in the group search functionality of the Keycloak server's administrative API. When Fine-Grained Admin Permissions (FGAP) v2 is enabled, a delegated administrator can bypass access restrictions to view parent groups they are not authorized to see. By searching for a child group they have permission to view, the system incorrectly returns the full details of the parent group in the response, leading to the disclosure of sensitive group attributes and configuration.

## References
- https://access.redhat.com/security/cve/CVE-2026-15945
- https://bugzilla.redhat.com/show_bug.cgi?id=2501302
- https://nvd.nist.gov/vuln/detail/CVE-2026-15945
