# [M] Exposure of Sensitive Information to an Unauthorized Actor in Keycloak

## Summary
Severity: Medium
Advisory: GHSA-xfqh-7356-vqjj
CVE: CVE-2019-14820
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2020-04-15
Source: https://github.com/advisories/GHSA-xfqh-7356-vqjj
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <8.0.0

## Details
It was found that keycloak before version 8.0.0 exposes internal adapter endpoints in org.keycloak.constants.AdapterConstants, which can be invoked via a specially-crafted URL. This vulnerability could allow an attacker to access unauthorized information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14820
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14820
