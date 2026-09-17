# [H] Authentication Bypass in keycloak

## Summary
Severity: High
Advisory: GHSA-m9cj-v55f-8x26
CVE: CVE-2020-27826
CWE: CWE-250
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-m9cj-v55f-8x26
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <12.0.0

## Details
A flaw was found in Keycloak before version 12.0.0 where it is possible to update the user's metadata attributes using Account REST API. This flaw allows an attacker to change its own NameID attribute to impersonate the admin user for any particular application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-27826
- https://github.com/keycloak/keycloak/commit/dae4a3eaf26590b8d441b8e4bec3b700ee303b72
- https://access.redhat.com/security/cve/cve-2020-27826
- https://bugzilla.redhat.com/show_bug.cgi?id=1905089
