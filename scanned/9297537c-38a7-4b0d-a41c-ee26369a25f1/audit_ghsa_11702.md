# [M] Keycloak has Improper Access Control that allows attackers with valid credentials to bypass the allowRemoteResourceManagement=false

## Summary
Severity: Medium
Advisory: GHSA-4pgc-gfrr-wcmg
CVE: CVE-2026-4628
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-4pgc-gfrr-wcmg
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0

## Details
A flaw was found in Keycloak. An improper Access Control vulnerability in Keycloak’s User-Managed Access (UMA) resource_set endpoint allows attackers with valid credentials to bypass the allowRemoteResourceManagement=false restriction. This occurs due to incomplete enforcement of access control checks on PUT operations to the resource_set endpoint. This issue enables unauthorized modification of protected resources, impacting data integrity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4628
- https://access.redhat.com/security/cve/CVE-2026-4628
- https://bugzilla.redhat.com/show_bug.cgi?id=2450240
- https://github.com/keycloak/keycloak
