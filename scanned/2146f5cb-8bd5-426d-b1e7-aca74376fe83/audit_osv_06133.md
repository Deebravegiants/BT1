# [M] Keycloak-services: keycloak-services: generic identity-provider creation can bind brokers to organizations without manage-organizations

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-18201
Aliases: CVE-2026-18201
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-18201
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.3

## Details
Keycloak provides a way to manage identity providers and organizations through its administrative API. A flaw was discovered where an administrator with permission to manage identity providers could link a new provider to an organization without having the required permissions to manage that organization. This could allow an unauthorized administrator to influence how users log into specific organizations.

## References
- https://access.redhat.com/security/cve/CVE-2026-18201
- https://bugzilla.redhat.com/show_bug.cgi?id=2508290
- https://nvd.nist.gov/vuln/detail/CVE-2026-18201
