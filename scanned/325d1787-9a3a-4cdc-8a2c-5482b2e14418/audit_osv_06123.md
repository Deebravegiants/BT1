# [M] Keycloak-services: keycloak-services: unbounded metric cardinality in user event metrics via request-controlled error text

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-16100
Aliases: CVE-2026-16100
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-16100
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=26.6.0 <26.6.5

## Details
A flaw was found in the user-event metrics recording of Keycloak. When metrics are enabled, the system records raw error messages from failed account operations as Prometheus metric labels. Because these error messages can include user-supplied input like nonexistent client IDs, an authenticated user can create a massive number of unique metric entries, eventually exhausting system memory and causing the service to crash or become unavailable.

## References
- https://access.redhat.com/errata/RHSA-2026:50848
- https://access.redhat.com/errata/RHSA-2026:50849
- https://access.redhat.com/security/cve/CVE-2026-16100
- https://bugzilla.redhat.com/show_bug.cgi?id=2501730
- https://nvd.nist.gov/vuln/detail/CVE-2026-16100
