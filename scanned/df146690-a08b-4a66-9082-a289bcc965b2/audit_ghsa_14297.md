# [M] Jenkins NeuVector Vulnerability Scanner Plugin disables SSL/TLS certificate and hostname validation

## Summary
Severity: Medium
Advisory: GHSA-r3mm-v4x7-2phm
CVE: CVE-2023-30517
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-r3mm-v4x7-2phm
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:neuvector-vulnerability-scanner` — affected >=0

## Details
Jenkins NeuVector Vulnerability Scanner Plugin 1.22 and earlier unconditionally disables SSL/TLS certificate and hostname validation when connecting to a configured NeuVector Vulnerability Scanner server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30517
- https://www.jenkins.io/security/advisory/2023-04-12/#SECURITY-2841
- http://www.openwall.com/lists/oss-security/2023/04/13/3
