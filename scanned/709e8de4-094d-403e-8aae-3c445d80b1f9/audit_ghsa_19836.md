# [M] Improper Authorization in Keycloak Organization Mapper Allows Unauthorized Organization Claims 

## Summary
Severity: Medium
Advisory: GHSA-gvgg-2r3r-53x7
CVE: CVE-2025-1391
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-10
Source: https://github.com/advisories/GHSA-gvgg-2r3r-53x7
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=26.1.0 <26.1.3
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.0.10

## Details
This vulnerability is caused by the improper mapping of users to organizations based solely on email/username patterns. The issue is limited to the token claim level, meaning the user is not truly added to the organization but may appear as such in applications relying on these claims. The risk increases in scenarios where self-registration is enabled and unrestricted, allowing an attacker to exploit the naming pattern. The issue is mitigated if admins restrict registration or use strict validation mechanisms.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-gvgg-2r3r-53x7
- https://nvd.nist.gov/vuln/detail/CVE-2025-1391
- https://github.com/keycloak/keycloak/commit/5aa2b4c75bb474303ab807017582bc01a9f7e378
- https://access.redhat.com/errata/RHSA-2025:2545
- https://access.redhat.com/security/cve/CVE-2025-1391
- https://bugzilla.redhat.com/show_bug.cgi?id=2346082
- https://github.com/keycloak/keycloak
