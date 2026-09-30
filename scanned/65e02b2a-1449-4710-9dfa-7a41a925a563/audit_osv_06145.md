# [H] Keycloak: group-admin escalation to realm-admin

## Summary
Severity: High
Advisory: BIT-keycloak-2026-9099
Aliases: CVE-2026-9099
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-keycloak-2026-9099
Type: osv

## Affected
- Bitnami: `keycloak` — affected >=26.6.0 <26.6.4

## Details
A flaw was found in Keycloak. A missing authorization check in the GroupResource.addChild() endpoint within the Admin REST API allows an authenticated user with limited administrative privileges to reparent any existing group. When Fine-Grained Admin Permissions v2 (FGAPv2) is enabled, an attacker with management rights over a single low-privilege group can reparent a highly privileged group (such as one possessing the realm-admin role) under their managed group.

Because group permissions follow a hierarchical structure, this action unauthorizedly grants the attacker management and password-reset capabilities over the members of the targeted privileged group. An attacker can exploit this to reset an administrator's password, compromise the account, and achieve a full realm takeover, leading to a complete compromise of confidentiality, integrity, and availability.

## References
- https://access.redhat.com/errata/RHSA-2026:30049
- https://access.redhat.com/errata/RHSA-2026:30050
- https://access.redhat.com/errata/RHSA-2026:30083
- https://access.redhat.com/errata/RHSA-2026:30084
- https://access.redhat.com/security/cve/CVE-2026-9099
- https://bugzilla.redhat.com/show_bug.cgi?id=2480182
- https://nvd.nist.gov/vuln/detail/CVE-2026-9099
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-9099.json
