# [M] Keycloak Affected by Broken Access Control Vulnerability in the UserManagedPermissionService

## Summary
Severity: Medium
Advisory: GHSA-fm6w-rrp3-2x4w
CVE: CVE-2025-14778
CWE: CWE-266
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-fm6w-rrp3-2x4w
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.2.13
- Maven: `org.keycloak:keycloak-services` — affected >=26.5.0 <26.5.3
- Maven: `org.keycloak:keycloak-services` — affected >=26.3.0 <26.4.9

## Details
A flaw was found in Keycloak. A significant Broken Access Control vulnerability exists in the UserManagedPermissionService (UMA Protection API). When updating or deleting a UMA policy associated with multiple resources, the authorization check only verifies the caller's ownership against the first resource in the policy's list. This allows a user (Owner A) who owns one resource (RA) to update a shared policy and modify authorization rules for other resources (e.g., RB) in that same policy, even if those other resources are owned by a different user (Owner B). This constitutes a horizontal privilege escalation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14778
- https://github.com/keycloak/keycloak/issues/46147
- https://github.com/keycloak/keycloak/pull/46154
- https://access.redhat.com/errata/RHSA-2026:2363
- https://access.redhat.com/errata/RHSA-2026:2364
- https://access.redhat.com/errata/RHSA-2026:2365
- https://access.redhat.com/errata/RHSA-2026:2366
- https://access.redhat.com/security/cve/CVE-2025-14778
- https://bugzilla.redhat.com/show_bug.cgi?id=2422600
- https://github.com/keycloak/keycloak
