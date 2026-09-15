# [M] Keycloak Account Resources user lookup contains broken access control

## Summary
Severity: Medium
Advisory: GHSA-933f-rg6j-f46p
CVE: CVE-2026-37981
CWE: CWE-1220
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-933f-rg6j-f46p
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.4.12
- Maven: `org.keycloak:keycloak-services` — affected >=26.5.0 <26.6.2

## Details
Keycloak's Account Resources user lookup endpoint allows a remote authenticated user, who owns at least one User-Managed Access (UMA) resource, to enumerate and harvest personally identifiable information (PII) for all realm users. By sending crafted requests with arbitrary usernames or email values, the endpoint returns full profile objects for unrelated users. This leads to broad profile-level information disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-37981
- https://github.com/keycloak/keycloak/issues/49116
- https://github.com/keycloak/keycloak/pull/49122
- https://github.com/keycloak/keycloak/commit/33f6f873fda2c9546e52d34b4f865eafc42df0c0
- https://github.com/keycloak/keycloak/commit/b68070bcf96a6fe7d0f01cee5d3cbde71f2abbe7
- https://access.redhat.com/errata/RHSA-2026:19596
- https://access.redhat.com/errata/RHSA-2026:19597
- https://access.redhat.com/security/cve/CVE-2026-37981
- https://bugzilla.redhat.com/show_bug.cgi?id=2455326
- https://github.com/keycloak/keycloak
