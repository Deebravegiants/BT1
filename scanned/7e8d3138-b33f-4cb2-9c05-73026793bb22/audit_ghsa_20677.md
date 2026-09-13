# [M] Keycloak has Files or Directories Accessible to External Parties

## Summary
Severity: Medium
Advisory: GHSA-3w4v-rvc4-2xpw
CVE: CVE-2021-3856
CWE: CWE-22, CWE-552
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-08-27
Source: https://github.com/advisories/GHSA-3w4v-rvc4-2xpw
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <15.1.0

## Details
ClassLoaderTheme and ClasspathThemeResourceProviderFactory allows reading any file available as a resource to the classloader. By sending requests for theme resources with a relative path from an external HTTP client, the client will receive the content of random files if available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3856
- https://github.com/keycloak/keycloak/pull/8588
- https://github.com/keycloak/keycloak/commit/73f0474008e1bebd0733e62a22aceda9e5de6743
- https://access.redhat.com/security/cve/CVE-2021-3856
- https://bugzilla.redhat.com/show_bug.cgi?id=2010164
- https://github.com/keycloak/keycloak
- https://issues.redhat.com/browse/KEYCLOAK-19422
