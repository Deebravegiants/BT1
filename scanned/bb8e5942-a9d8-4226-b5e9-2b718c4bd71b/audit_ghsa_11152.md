# [H] Keycloak allows authentication using an Identity Provider (IdP) even after it has been disabled by an administrator

## Summary
Severity: High
Advisory: GHSA-m297-3jv9-m927
CVE: CVE-2026-3009
CWE: CWE-285, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-m297-3jv9-m927
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.5.5

## Details
A security flaw in the IdentityBrokerService.performLogin endpoint of Keycloak allows authentication to proceed using an Identity Provider (IdP) even after it has been disabled by an administrator. An attacker who knows the IdP alias can reuse a previously generated login request to bypass the administrative restriction. This undermines access control enforcement and may allow unauthorized authentication through a disabled external provider.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3009
- https://github.com/keycloak/keycloak/issues/46911
- https://github.com/keycloak/keycloak/commit/4fd5367e6cc28cfa68fb2240fc459c12b1fdbf2a
- https://access.redhat.com/errata/RHSA-2026:3947
- https://access.redhat.com/errata/RHSA-2026:3948
- https://access.redhat.com/security/cve/CVE-2026-3009
- https://bugzilla.redhat.com/show_bug.cgi?id=2441867
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/releases/tag/26.5.5
