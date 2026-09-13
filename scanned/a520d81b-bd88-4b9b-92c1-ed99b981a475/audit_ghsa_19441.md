# [M] Keycloak vulnerable to two factor authentication bypass

## Summary
Severity: Medium
Advisory: GHSA-5jfq-x6xp-7rw2
CVE: CVE-2025-3910
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-30
Source: https://github.com/advisories/GHSA-5jfq-x6xp-7rw2
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.2.2

## Details
# Description
A flaw was found in Keycloak. The org.keycloak.authorization package may be vulnerable to circumventing required actions, allowing users to circumvent requirements such as setting up two-factor authentication.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-5jfq-x6xp-7rw2
- https://nvd.nist.gov/vuln/detail/CVE-2025-3910
- https://github.com/keycloak/keycloak/issues/39349
- https://access.redhat.com/errata/RHSA-2025:4335
- https://access.redhat.com/errata/RHSA-2025:4336
- https://access.redhat.com/security/cve/CVE-2025-3910
- https://bugzilla.redhat.com/show_bug.cgi?id=2361923
- https://github.com/keycloak/keycloak
