# [C] Keycloak vulnerable to cross-site scripting when validating URI-schemes on SAML and OIDC

## Summary
Severity: Critical
Advisory: GHSA-3p62-6fjh-3p5h
CVE: CVE-2022-4361
CWE: CWE-79, CWE-81
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-30
Source: https://github.com/advisories/GHSA-3p62-6fjh-3p5h
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <21.1.2

## Details
AssertionConsumerServiceURL is a Java implementation for SAML Service Providers (org.keycloak.protocol.saml). Affected versions of this package are vulnerable to Cross-site Scripting (XSS).

AssertionConsumerServiceURL allows XSS when sending a crafted SAML XML request.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-3p62-6fjh-3p5h
- https://nvd.nist.gov/vuln/detail/CVE-2022-4361
- https://github.com/keycloak/keycloak/commit/a1cfe6e24e5b34792699a00b8b4a8016a5929e3a
- https://bugzilla.redhat.com/show_bug.cgi?id=2151618
- https://github.com/keycloak/keycloak
