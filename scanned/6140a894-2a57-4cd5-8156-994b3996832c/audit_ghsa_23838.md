# [H] Keycloak Authentication Error

## Summary
Severity: High
Advisory: GHSA-fv4q-wm8c-wjg4
CVE: CVE-2019-14909
CWE: CWE-287, CWE-305
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fv4q-wm8c-wjg4
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=7.0.0

## Details
A vulnerability was found in Keycloak 7.x where the user federation LDAP bind type is none (LDAP anonymous bind), any password, invalid or valid will be accepted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14909
- https://access.redhat.com/security/cve/cve-2019-14909
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14909
- https://github.com/keycloak/keycloak
