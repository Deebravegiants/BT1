# [H] Keycloak: Application-Level DoS via Scope Processing

## Summary
Severity: High
Advisory: GHSA-h4wv-g838-66g3
CVE: CVE-2026-4634
CWE: CWE-1050
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-h4wv-g838-66g3
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.5.7

## Details
A flaw was found in Keycloak. An unauthenticated attacker can exploit this vulnerability by sending a specially crafted POST request with an excessively long scope parameter to the OpenID Connect (OIDC) token endpoint. This leads to high resource consumption and prolonged processing times, ultimately resulting in a Denial of Service (DoS) for the Keycloak server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4634
- https://github.com/keycloak/keycloak/issues/47716
- https://github.com/keycloak/keycloak/commit/b455ee4f28abb6f2120aff72fd179589cc5267a0
- https://access.redhat.com/errata/RHSA-2026:6475
- https://access.redhat.com/errata/RHSA-2026:6476
- https://access.redhat.com/errata/RHSA-2026:6477
- https://access.redhat.com/errata/RHSA-2026:6478
- https://access.redhat.com/security/cve/CVE-2026-4634
- https://bugzilla.redhat.com/show_bug.cgi?id=2450250
- https://github.com/keycloak/keycloak
