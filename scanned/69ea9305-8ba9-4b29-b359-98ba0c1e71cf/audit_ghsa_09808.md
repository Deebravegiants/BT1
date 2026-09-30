# [H] Keycloak: Privilege escalation via forged authorization codes due to SingleUseObjectProvider isolation flaw

## Summary
Severity: High
Advisory: GHSA-hj93-h7pg-fh6v
CVE: CVE-2026-4282
CWE: CWE-653
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-hj93-h7pg-fh6v
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.5.7

## Details
A flaw was found in Keycloak. The SingleUseObjectProvider, a global key-value store, lacks proper type and namespace isolation. This vulnerability allows an unauthenticated attacker to forge authorization codes. Successful exploitation can lead to the creation of admin-capable access tokens, resulting in privilege escalation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4282
- https://github.com/keycloak/keycloak/issues/47719
- https://github.com/keycloak/keycloak/commit/9046f201125a6fd6be9c116b99d348509d99d4a5
- https://access.redhat.com/errata/RHSA-2026:6475
- https://access.redhat.com/errata/RHSA-2026:6476
- https://access.redhat.com/errata/RHSA-2026:6477
- https://access.redhat.com/errata/RHSA-2026:6478
- https://access.redhat.com/security/cve/CVE-2026-4282
- https://bugzilla.redhat.com/show_bug.cgi?id=2448061
- https://github.com/keycloak/keycloak
