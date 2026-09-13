# [M] Keycloak vulnerable to session takeovers due to reuse of session identifiers

## Summary
Severity: Medium
Advisory: GHSA-rg35-5v25-mqvp
CVE: CVE-2025-12390
CWE: CWE-384
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-10-28
Source: https://github.com/advisories/GHSA-rg35-5v25-mqvp
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.0.0

## Details
A flaw was found in Keycloak. In Keycloak where a user can accidentally get access to another user's session if both use the same device and browser. This happens because Keycloak sometimes reuses session identifiers and doesn’t clean up properly during logout when browser cookies are missing. As a result, one user may receive tokens that belong to another user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12390
- https://github.com/keycloak/keycloak/issues/32197
- https://github.com/keycloak/keycloak/issues/43853
- https://github.com/keycloak/keycloak/commit/5344aada5ee06b02ec3a9e0f52fa381d085b6282
- https://github.com/keycloak/keycloak/commit/b46fab230824a2304daafe74be019e8bd4ee590a
- https://github.com/keycloak/keycloak/commit/d82438a611f2f869f1966c13012953fe963a493d
- https://github.com/keycloak/keycloak/commit/ef75a4dc50aa9459777494e4b88655100bf2ac80
- https://access.redhat.com/errata/RHSA-2025:21370
- https://access.redhat.com/errata/RHSA-2025:21371
- https://access.redhat.com/errata/RHSA-2025:22088
- https://access.redhat.com/errata/RHSA-2025:22089
- https://access.redhat.com/security/cve/CVE-2025-12390
- https://bugzilla.redhat.com/show_bug.cgi?id=2406793
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/discussions/31265
