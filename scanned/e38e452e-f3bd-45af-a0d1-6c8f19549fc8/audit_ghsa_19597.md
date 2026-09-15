# [H] Keycloak hostname verification

## Summary
Severity: High
Advisory: GHSA-hw58-3793-42gg
CVE: CVE-2025-3501
CWE: CWE-297
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-04-30
Source: https://github.com/advisories/GHSA-hw58-3793-42gg
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.2.2

## Details
A flaw was found in Keycloak. By setting a verification policy to 'ANY', the trust store certificate verification is skipped, which is unintended.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-hw58-3793-42gg
- https://nvd.nist.gov/vuln/detail/CVE-2025-3501
- https://github.com/keycloak/keycloak/issues/39350
- https://github.com/keycloak/keycloak/pull/39366
- https://github.com/keycloak/keycloak/commit/99ca24c832729075e04d8bc58666089268314272
- https://access.redhat.com/errata/RHSA-2025:4335
- https://access.redhat.com/errata/RHSA-2025:4336
- https://access.redhat.com/security/cve/CVE-2025-3501
- https://bugzilla.redhat.com/show_bug.cgi?id=2358834
- https://github.com/keycloak/keycloak
