# [M] Improper Authentication for Keycloak

## Summary
Severity: Medium
Advisory: GHSA-j229-2h63-rvh9
CVE: CVE-2020-1718
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-j229-2h63-rvh9
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=0 <8.0.0

## Details
A flaw was found in the reset credential flow in all Keycloak versions before 8.0.0. This flaw allows an attacker to gain unauthorized access to the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1718
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-1718
