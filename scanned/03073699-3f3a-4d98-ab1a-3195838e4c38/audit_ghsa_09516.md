# [M] Keycloak Protection API allows authenticated clients to access and modify resources owned by other Resource Servers

## Summary
Severity: Medium
Advisory: GHSA-c739-f6xw-6pv2
CVE: CVE-2026-4630
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-c739-f6xw-6pv2
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.6.2

## Details
Keycloak's Authorization Services feature exposes a User-Managed Access Protection API that include an Insecure Direct Object Reference (IDOR) vulnerability in the Authorization Services Protection API endpoint. By knowing or obtaining a resource's unique identifier (UUID) belonging to another Resource Server within the same realm, an authenticated client could bypass authorization checks. This allows the client to perform unauthorized GET, PUT, and DELETE operations on resources, leading to information disclosure and potential unauthorized modification or deletion of data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4630
- https://github.com/keycloak/keycloak/issues/49115
- https://github.com/keycloak/keycloak/pull/49121
- https://github.com/keycloak/keycloak/commit/0cea089bd19f5061f5fd47099fd6fb41a17d8c55
- https://github.com/keycloak/keycloak/commit/1192267af8f16a7b722bdc2abbd3410c477388aa
- https://github.com/keycloak/keycloak/commit/4e9b17cbedb828b4afc6b62399eee317d4735234
- https://access.redhat.com/errata/RHSA-2026:19596
- https://access.redhat.com/errata/RHSA-2026:19597
- https://access.redhat.com/security/cve/CVE-2026-4630
- https://bugzilla.redhat.com/show_bug.cgi?id=2450245
- https://github.com/keycloak/keycloak
