# [C] Keycloak Authentication Error

## Summary
Severity: Critical
Advisory: GHSA-jf86-9434-f8c2
CVE: CVE-2019-14910
CWE: CWE-278, CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jf86-9434-f8c2
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=7.0.0

## Details
A vulnerability was found in keycloak 7.x, when keycloak is configured with LDAP user federation and StartTLS is used instead of SSL/TLS from the LDAP server (ldaps), in this case user authentication succeeds even if invalid password has entered.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14910
- https://access.redhat.com/security/cve/cve-2019-14910
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14910
- https://github.com/keycloak/keycloak
