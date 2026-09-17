# [M] Keycloak Admin UI REST Extensions: bulk role-removal endpoints fail to perform granular permission checks

## Summary
Severity: Medium
Advisory: GHSA-6w3v-mcfh-m3q7
CVE: CVE-2026-11986
CWE: CWE-425
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-6w3v-mcfh-m3q7
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-rest-admin-ui-ext` — affected >=0 <26.7.0

## Details
A flaw was found in the admin-ui-ext component of Keycloak, which provides extended administrative user interface capabilities. The issue occurs because certain bulk role-removal endpoints fail to perform granular permission checks when deleting role mappings. This allows a delegated administrator with limited permissions to remove highly privileged roles from other users or groups, potentially disrupting administrative access control.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-11986
- https://github.com/keycloak/keycloak/issues/49766
- https://github.com/keycloak/keycloak/pull/49826
- https://github.com/keycloak/keycloak/commit/f3831f01fd4abceb47e9675ab5f4c17268ba9e9d
- https://access.redhat.com/errata/RHSA-2026:50848
- https://access.redhat.com/errata/RHSA-2026:50849
- https://access.redhat.com/security/cve/CVE-2026-11986
- https://bugzilla.redhat.com/show_bug.cgi?id=2487906
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/releases/tag/26.7.0
