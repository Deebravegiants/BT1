# [H] Keycloak has privilege escalation via improper scope mapping enforcement

## Summary
Severity: High
Advisory: GHSA-32h4-44jj-c5vx
CVE: CVE-2026-9795
CWE: CWE-266
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-32h4-44jj-c5vx
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.6.4

## Details
### Description
A flaw was found in Keycloak's Fine-Grained Admin Permissions (FGAPv2) feature. An administrator with limited client management permissions can exploit this vulnerability to assign any realm role, including highly privileged roles, to a client's scope mapping. This bypasses intended security controls, allowing the injected role to be projected into a user's authentication token when they access the modified client. This could lead to unauthorized privilege escalation within the Keycloak realm.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-32h4-44jj-c5vx
- https://nvd.nist.gov/vuln/detail/CVE-2026-9795
- https://github.com/keycloak/keycloak/issues/50350
- https://github.com/keycloak/keycloak/pull/50451
- https://github.com/keycloak/keycloak/commit/8894c027e788904c740ff9a1a60fcfaa34a10d13
- https://access.redhat.com/errata/RHSA-2026:30049
- https://access.redhat.com/errata/RHSA-2026:30050
- https://access.redhat.com/errata/RHSA-2026:30083
- https://access.redhat.com/errata/RHSA-2026:30084
- https://access.redhat.com/security/cve/CVE-2026-9795
- https://bugzilla.redhat.com/show_bug.cgi?id=2482462
- https://github.com/keycloak/keycloak
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-9795.json
