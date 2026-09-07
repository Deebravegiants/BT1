# [H] Improper Input Validation and Cross-Site Request Forgery in Keycloak

## Summary
Severity: High
Advisory: GHSA-p5xp-6vpf-jwvh
CVE: CVE-2019-10199
CWE: CWE-20, CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-09-23
Source: https://github.com/advisories/GHSA-p5xp-6vpf-jwvh
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <7.0.0

## Details
It was found that Keycloak's account console, up to 6.0.1, did not perform adequate header checks in some requests. An attacker could use this flaw to trick an authenticated user into performing operations via request from an untrusted domain.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10199
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10199
- https://github.com/keycloak/keycloak
