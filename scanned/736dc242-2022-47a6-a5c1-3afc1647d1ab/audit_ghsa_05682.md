# [M] Keycloak has Incorrect Behavior Order: Authorization Before Parsing and Canonicalization

## Summary
Severity: Medium
Advisory: GHSA-gv94-wp4h-vv8p
CVE: CVE-2026-0707
CWE: CWE-551
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-gv94-wp4h-vv8p
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=0

## Details
A flaw was found in Keycloak. The Keycloak Authorization header parser is overly permissive regarding the formatting of the "Bearer" authentication scheme. It accepts non-standard characters (such as tabs) as separators and tolerates case variations that deviate from RFC 6750 specifications.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-0707
- https://github.com/keycloak/keycloak/issues/49433
- https://access.redhat.com/errata/RHSA-2026:3947
- https://access.redhat.com/errata/RHSA-2026:3948
- https://access.redhat.com/security/cve/CVE-2026-0707
- https://bugzilla.redhat.com/show_bug.cgi?id=2427768
- https://github.com/keycloak/keycloak
