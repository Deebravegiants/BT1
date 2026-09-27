# [M] Keycloak users may be able to remove MFA from other users' devices

## Summary
Severity: Medium
Advisory: GHSA-9695-w6h2-jpv9
CVE: CVE-2020-10686
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9695-w6h2-jpv9
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <9.0.2

## Details
A community-only flaw was found where a malicious user can register himself and then uses the "remove devices" form to post different credential ids with the hope of removing MFA devices for other users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10686
- https://github.com/keycloak/keycloak/commit/5ddd605ee96b8551c7eb00b609a0b97939925b77
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10686
- https://github.com/keycloak/keycloak
