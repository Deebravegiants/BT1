# [M] Keycloak LDAP User Federation provider enables admin-triggered untrusted Java deserialization

## Summary
Severity: Medium
Advisory: GHSA-4hx9-48xh-5mxr
CVE: CVE-2025-13467
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-12-19
Source: https://github.com/advisories/GHSA-4hx9-48xh-5mxr
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-ldap-federation` — affected >=26.3.0 <26.4.6
- Maven: `org.keycloak:keycloak-ldap-federation` — affected >=0 <26.2.11

## Details
A flaw was found in the Keycloak LDAP User Federation provider. This vulnerability allows an authenticated realm administrator to trigger deserialization of untrusted Java objects via a malicious LDAP server configuration.

### Mitigation

Disable LDAP referrals in all LDAP user providers in all realms if projects cannot upgrade to the patched versions.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-4hx9-48xh-5mxr
- https://nvd.nist.gov/vuln/detail/CVE-2025-13467
- https://github.com/keycloak/keycloak/issues/44478
- https://github.com/keycloak/keycloak/commit/754c070cf8ca187dcc71f0f72ff3130ff2195328
- https://github.com/keycloak/keycloak/commit/b90fec41ff17a70858d830750156a8a2e13ddb82
- https://access.redhat.com/errata/RHSA-2025:22088
- https://access.redhat.com/security/cve/CVE-2025-13467
- https://bugzilla.redhat.com/show_bug.cgi?id=2416038
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/releases/tag/26.4.6
