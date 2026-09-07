# [M] Cross-site Scripting in Keycloak

## Summary
Severity: Medium
Advisory: GHSA-hgpg-593r-hhvp
CVE: CVE-2020-10748
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-hgpg-593r-hhvp
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=0 <10.0.2

## Details
A flaw was found in Keycloak's data filter, in version 10.0.1, where it allowed the processing of data URLs in some circumstances. This flaw allows an attacker to conduct cross-site scripting or further attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10748
- https://bugzilla.redhat.com/show_bug.cgi?id=1836786
