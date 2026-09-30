# [M] Keycloak secondary factor bypass in step-up authentication

## Summary
Severity: Medium
Advisory: GHSA-4f53-xh3v-g8x4
CVE: CVE-2023-3597
CWE: CWE-287, CWE-288
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-04-17
Source: https://github.com/advisories/GHSA-4f53-xh3v-g8x4
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <22.0.10
- Maven: `org.keycloak:keycloak-services` — affected >=23.0.0 <24.0.3

## Details
Keycloak does not correctly validate its client step-up authentication. A password-authed attacker could use this flaw to register a false second auth factor, alongside the existing one, to a targeted account. The second factor then permits step-up authentication.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-4f53-xh3v-g8x4
- https://nvd.nist.gov/vuln/detail/CVE-2023-3597
- https://github.com/keycloak/keycloak/commit/aa634aee882892960a526e49982806e103c8a432
- https://access.redhat.com/errata/RHSA-2024:1866
- https://access.redhat.com/errata/RHSA-2024:1867
- https://access.redhat.com/errata/RHSA-2024:1868
- https://access.redhat.com/security/cve/CVE-2023-3597
- https://bugzilla.redhat.com/show_bug.cgi?id=2221760
- https://github.com/keycloak/keycloak
