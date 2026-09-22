# [H] Keycloak fails to verify if an Identity Provider (IdP) is enabled before issuing tokens

## Summary
Severity: High
Advisory: GHSA-37gf-gmxv-74wv
CVE: CVE-2026-1486
CWE: CWE-358
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-37gf-gmxv-74wv
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=26.5.0 <26.5.3
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.4.9

## Details
A flaw was found in Keycloak. A vulnerability exists in the jwt-authorization-grant flow where the server fails to verify if an Identity Provider (IdP) is enabled before issuing tokens. The issuer lookup mechanism (lookupIdentityProviderFromIssuer) retrieves the IdP configuration but does not filter for isEnabled=false. If an administrator disables an IdP (e.g., due to a compromise or offboarding), an entity possessing that IdP's signing key can still generate valid JWT assertions that Keycloak accepts, resulting in the issuance of valid access tokens.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1486
- https://github.com/keycloak/keycloak/issues/46146
- https://github.com/keycloak/keycloak/pull/46148
- https://github.com/keycloak/keycloak/commit/176dc8902ce552056d3648c4601d519afc6fb043
- https://github.com/keycloak/keycloak/commit/8316e8538f0037d9f998181e73122cff93a94035
- https://access.redhat.com/errata/RHSA-2026:2365
- https://access.redhat.com/errata/RHSA-2026:2366
- https://access.redhat.com/security/cve/CVE-2026-1486
- https://bugzilla.redhat.com/show_bug.cgi?id=2433347
- https://github.com/keycloak/keycloak
