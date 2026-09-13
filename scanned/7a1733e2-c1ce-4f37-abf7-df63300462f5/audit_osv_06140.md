# [M] Keycloak-services: keycloak-services: uma claim token can override authorization time-policy evaluation attributes

## Summary
Severity: Medium
Advisory: BIT-keycloak-2026-18572
Aliases: CVE-2026-18572
Ecosystem: Bitnami
Published: 2026-08-31
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-18572
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=0 <26.7.3

## Details
Keycloak provides authorization services that allow administrators to restrict access to resources based on time policies (for example, only allowing access during business hours). A flaw was discovered where a user can include a fake time value in their authorization request that overrides the actual server time. This allows the user to bypass these time-based restrictions and access protected resources at unauthorized times.

## References
- https://access.redhat.com/security/cve/CVE-2026-18572
- https://bugzilla.redhat.com/show_bug.cgi?id=2509763
- https://nvd.nist.gov/vuln/detail/CVE-2026-18572
