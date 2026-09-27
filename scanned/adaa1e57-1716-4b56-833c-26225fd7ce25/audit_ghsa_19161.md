# [M] Keycloak on Quarkus CLI option for encrypted JGroups ignored

## Summary
Severity: Medium
Advisory: GHSA-g6qq-c9f9-2772
CVE: CVE-2024-10973
CWE: CWE-319
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-02-05
Source: https://github.com/advisories/GHSA-g6qq-c9f9-2772
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-quarkus-server` — affected >=25.0.0 <26.0.6

## Details
The env option `KC_CACHE_EMBEDDED_MTLS_ENABLED` does not work and the jgroups replication configuration is always used in plain. This option worked before in 24 and 22. More info in public issue https://github.com/keycloak/keycloak/issues/34644.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-g6qq-c9f9-2772
- https://nvd.nist.gov/vuln/detail/CVE-2024-10973
- https://github.com/keycloak/keycloak/issues/28750
- https://github.com/keycloak/keycloak/issues/34644
- https://github.com/keycloak/keycloak/pull/28756
- https://github.com/keycloak/keycloak/pull/34668
- https://github.com/keycloak/keycloak/commit/071032a108bd9e9fce9e66d00c36d56bd4b334df
- https://github.com/keycloak/keycloak/commit/36defd5f33b2da5d705f179bbaa21c28b13a9996
- https://access.redhat.com/security/cve/CVE-2024-10973
- https://bugzilla.redhat.com/show_bug.cgi?id=2324361
- https://github.com/keycloak/keycloak
