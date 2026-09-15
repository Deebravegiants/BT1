# [M] Missing Authorization in Jenkins Blue Ocean Plugin

## Summary
Severity: Medium
Advisory: GHSA-phf8-3qgv-rg5q
CVE: CVE-2017-1000105
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-phf8-3qgv-rg5q
Type: github-advisory

## Affected
- Maven: `io.jenkins.blueocean:blueocean` — affected >=0

## Details
The optional Run/Artifacts permission can be enabled by setting a Java system property.

Blue Ocean did not check this permission before providing access to archived artifacts, Item/Read permission was sufficient.

Blue Ocean now correctly checks the Run/Artifacts permission if it’s enabled before providing access to artifacts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000105
- https://jenkins.io/security/advisory/2017-08-07
