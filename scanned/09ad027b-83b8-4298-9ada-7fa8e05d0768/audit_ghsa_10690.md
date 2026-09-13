# [M] Keycloak: Replay of action tokens via improper handling of single-use entries

## Summary
Severity: Medium
Advisory: GHSA-rx66-hj7g-28h7
CVE: CVE-2026-4325
CWE: CWE-653
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-rx66-hj7g-28h7
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.5.7

## Details
A flaw was found in Keycloak. The SingleUseObjectProvider, a global key-value store, lacks proper type and namespace isolation. This vulnerability allows an attacker to delete arbitrary single-use entries, which can enable the replay of consumed action tokens, such as password reset links. This could lead to unauthorized access or account compromise.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4325
- https://github.com/keycloak/keycloak/issues/47715
- https://github.com/keycloak/keycloak/commit/9046f201125a6fd6be9c116b99d348509d99d4a5
- https://access.redhat.com/errata/RHSA-2026:6475
- https://access.redhat.com/errata/RHSA-2026:6476
- https://access.redhat.com/errata/RHSA-2026:6477
- https://access.redhat.com/errata/RHSA-2026:6478
- https://access.redhat.com/security/cve/CVE-2026-4325
- https://bugzilla.redhat.com/show_bug.cgi?id=2448351
- https://github.com/keycloak/keycloak
