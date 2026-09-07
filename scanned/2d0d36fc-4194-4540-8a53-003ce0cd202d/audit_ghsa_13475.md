# [M] Keycloak: Impersonation and lockout possible through incorrect handling of email trust

## Summary
Severity: Medium
Advisory: GHSA-c7xw-p58w-h6fj
CVE: CVE-2023-0105
CWE: CWE-287, CWE-841
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2023-07-18
Source: https://github.com/advisories/GHSA-c7xw-p58w-h6fj
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <22.0.1

## Details
Impersonation and lockout are possible due to email trust not being handled correctly in Keycloak. Since the verified state is not reset when the email changes, it is possible for users to shadow others with the same email and lock out or impersonate them.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-c7xw-p58w-h6fj
- https://github.com/keycloak/keycloak/commit/87a50d3ba790b049e436c9925874f9b418af7988
- https://access.redhat.com/security/cve/CVE-2023-0105
- https://bugzilla.redhat.com/show_bug.cgi?id=2158910
- https://github.com/keycloak/keycloak
