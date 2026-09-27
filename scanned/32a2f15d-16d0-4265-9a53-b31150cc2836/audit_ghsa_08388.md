# [H] Keycloak: Access token disclosure and implicit flow bypass via forged client data

## Summary
Severity: High
Advisory: GHSA-hq3p-w4xv-x7vp
CVE: CVE-2026-7571
CWE: CWE-472
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-hq3p-w4xv-x7vp
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.6.2

## Details
A flaw was found in Keycloak. A low-privilege user, with knowledge of user credentials and client ID, can bypass a security control intended to disable the implicit flow in OpenID Connect (OIDC) clients. By manipulating client data during a session restart, an attacker can obtain an access token that should not be available. This vulnerability can also lead to the exposure of these access tokens in server logs, proxy logs, and HTTP Referrer headers, resulting in sensitive information disclosure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7571
- https://github.com/keycloak/keycloak/issues/49110
- https://github.com/keycloak/keycloak/pull/49120
- https://github.com/keycloak/keycloak/commit/56bbfa3d8abccf39df787ae73e044a75aba1da13
- https://access.redhat.com/errata/RHSA-2026:19596
- https://access.redhat.com/errata/RHSA-2026:19597
- https://access.redhat.com/security/cve/CVE-2026-7571
- https://bugzilla.redhat.com/show_bug.cgi?id=2464263
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/releases/tag/26.6.2
