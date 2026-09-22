# [M] Incorrect Authorization in keycloak

## Summary
Severity: Medium
Advisory: GHSA-p225-pc2x-4jpm
CVE: CVE-2020-1725
CWE: CWE-668, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-p225-pc2x-4jpm
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=0 <13.0.0

## Details
A flaw was found in keycloak before version 13.0.0. In some scenarios a user still has access to a resource after changing the role mappings in Keycloak and after expiration of the previous access token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1725
- https://bugzilla.redhat.com/show_bug.cgi?id=1765129
- https://issues.redhat.com/browse/KEYCLOAK-16550
