# [M] ONOS vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-q63q-hwf6-3mw6
CVE: CVE-2023-30093
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-05
Source: https://github.com/advisories/GHSA-q63q-hwf6-3mw6
Type: github-advisory

## Affected
- Maven: `org.onosproject:onos-archetypes` — affected >=1.9.0

## Details
A cross-site scripting (XSS) vulnerability in Open Network Operating System (ONOS) from version v1.9.0 to v2.7.0 allows attackers to execute arbitrary web scripts or HTML via a crafted payload injected into the authorizationURL parameter of the API documentation dashboard under securityDefinitions > OAuth2 > authorizationURL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30093
- https://github.com/opennetworkinglab/onos
- https://www.edoardoottavianelli.it/CVE-2023-30093
- https://www.youtube.com/watch?v=jZr2JhDd_S8
