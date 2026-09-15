# [M] Keycloak Path Traversal Vulnerability Due to External Control of File Name or Path

## Summary
Severity: Medium
Advisory: GHSA-5545-r4hg-rj4m
CVE: CVE-2024-10492
CWE: CWE-73
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-11-25
Source: https://github.com/advisories/GHSA-5545-r4hg-rj4m
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-quarkus-server` — affected >=0 <26.0.6
- Maven: `org.keycloak:keycloak-quarkus-server` — affected >=25.0.0 <26.0.6

## Details
A vulnerability was found in Keycloak. A user with high privileges could read sensitive information from a Vault file that is not within the expected context. This attacker must have previous high access to the Keycloak server in order to perform resource creation, for example, an LDAP provider configuration and set up a Vault read file, which will only inform whether that file exists or not.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-5545-r4hg-rj4m
- https://nvd.nist.gov/vuln/detail/CVE-2024-10492
- https://github.com/keycloak/keycloak/issues/35215
- https://github.com/keycloak/keycloak/commit/d60cb9aaefc4035d322862edd8f9f252af6da951
- https://access.redhat.com/errata/RHSA-2024:10175
- https://access.redhat.com/errata/RHSA-2024:10176
- https://access.redhat.com/errata/RHSA-2024:10177
- https://access.redhat.com/errata/RHSA-2024:10178
- https://access.redhat.com/security/cve/CVE-2024-10492
- https://bugzilla.redhat.com/show_bug.cgi?id=2322447
- https://github.com/keycloak/keycloak
