# [M] Jenkins Bumblebee HP ALM Plugin unconditionally disabled SSL/TLS certificate validation

## Summary
Severity: Medium
Advisory: GHSA-qgp8-h5cp-r75r
CVE: CVE-2019-10444
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qgp8-h5cp-r75r
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:bumblebee` — affected >=0 <4.1.4

## Details
Jenkins Bumblebee HP ALM Plugin unconditionally disabled SSL/TLS certificate validation for connections to the HP ALM service.

Bumblebee HP ALM Plugin no longer does that. Instead, it now allows users to opt out of certificate validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10444
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1481
