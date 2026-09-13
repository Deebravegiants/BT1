# [M] Keycloak has a Forced Browsing issue

## Summary
Severity: Medium
Advisory: GHSA-hm32-hfmw-rhvg
CVE: CVE-2026-7500
CWE: CWE-425
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-30
Source: https://github.com/advisories/GHSA-hm32-hfmw-rhvg
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0

## Details
When Keycloak is started with `--features-disabled=account,account-api`, the Account REST API is only partially disabled. Five endpoints under the versioned path `/account/v1alpha1` remain fully functional — including both read and write operations — because they lack the `checkAccountApiEnabled()` gate that correctly blocks four other endpoints in the same REST service class. The user needs to have permissions to use the API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7500
- https://github.com/keycloak/keycloak/issues/48709
- https://github.com/keycloak/keycloak/pull/48715
- https://access.redhat.com/errata/RHSA-2026:25097
- https://access.redhat.com/errata/RHSA-2026:25098
- https://access.redhat.com/errata/RHSA-2026:30049
- https://access.redhat.com/errata/RHSA-2026:30050
- https://access.redhat.com/security/cve/CVE-2026-7500
- https://bugzilla.redhat.com/show_bug.cgi?id=2464126
- https://github.com/keycloak/keycloak
