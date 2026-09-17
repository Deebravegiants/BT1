# [H] keycloak-httpd-client-install Insecure Secrets

## Summary
Severity: High
Advisory: GHSA-89c9-3758-737w
CVE: CVE-2017-15112
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-89c9-3758-737w
Type: github-advisory

## Affected
- PyPI: `keycloak-httpd-client-install` — affected >=0 <0.8

## Details
keycloak-httpd-client-install versions before 0.8 allow users to insecurely pass password through command line, leaking it via command history and process info to other local users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15112
- https://github.com/jdennis/keycloak-httpd-client-install/commit/c3121b271abaaa1a76de2b9ae89dacde0105cd75
- https://access.redhat.com/errata/RHSA-2019:2137
- https://github.com/jdennis/keycloak-httpd-client-install
