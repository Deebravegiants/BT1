# [H] Improper privilege management in Keycloak

## Summary
Severity: High
Advisory: GHSA-c9x9-xv66-xp3v
CVE: CVE-2020-14389
CWE: CWE-269, CWE-916
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-c9x9-xv66-xp3v
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <12.0.0

## Details
A flaw was found in Keycloak, where it would permit a user with a view-profile role to manage the resources in the new account console. This flaw allows a user with a view-profile role to access and modify data for which the user does not have adequate permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14389
- https://access.redhat.com/security/cve/cve-2020-14389
