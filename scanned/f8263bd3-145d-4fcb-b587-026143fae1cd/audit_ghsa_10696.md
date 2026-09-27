# [H] Keycloak: Redirect URI validation bypass via ..;/ path traversal in OIDC auth endpoint

## Summary
Severity: High
Advisory: GHSA-cjm2-j6cm-6p6m
CVE: CVE-2026-3872
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-cjm2-j6cm-6p6m
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.5.7

## Details
A flaw was found in Keycloak. This issue allows an attacker, who controls another path on the same web server, to bypass the allowed path in redirect Uniform Resource Identifiers (URIs) that use a wildcard. A successful attack may lead to the theft of an access token, resulting in information disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3872
- https://github.com/keycloak/keycloak/issues/47718
- https://github.com/keycloak/keycloak/commit/35a71b00bc856ac402711130f60190d3a24795e7
- https://access.redhat.com/errata/RHSA-2026:6475
- https://access.redhat.com/errata/RHSA-2026:6476
- https://access.redhat.com/errata/RHSA-2026:6477
- https://access.redhat.com/errata/RHSA-2026:6478
- https://access.redhat.com/security/cve/CVE-2026-3872
- https://bugzilla.redhat.com/show_bug.cgi?id=2445988
- https://github.com/keycloak/keycloak
