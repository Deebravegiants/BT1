# [M] Authentication Bypass Due to Missing LDAP Bind After Password Reset in Keycloak

## Summary
Severity: Medium
Advisory: GHSA-2p82-5wwr-43cw
CVE: CVE-2025-0604
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-10
Source: https://github.com/advisories/GHSA-2p82-5wwr-43cw
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-ldap-federation` — affected >=26.1.0 <26.1.3
- Maven: `org.keycloak:keycloak-ldap-federation` — affected >=0 <26.0.10

## Details
The issue arises because Keycloak does not perform an LDAP bind after a password reset, leading to potential authentication bypass for expired or disabled AD accounts. A fix should enforce LDAP validation after password updates to ensure consistency with AD authentication policies.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-2p82-5wwr-43cw
- https://nvd.nist.gov/vuln/detail/CVE-2025-0604
- https://access.redhat.com/errata/RHSA-2025:2545
- https://access.redhat.com/security/cve/CVE-2025-0604
- https://bugzilla.redhat.com/show_bug.cgi?id=2338993
- https://github.com/keycloak/keycloak
