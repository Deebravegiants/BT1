# [M] Incorrect permission checks in Qualys Web App Scanning Connector Plugin allow capturing credentials 

## Summary
Severity: Medium
Advisory: GHSA-8wgf-3mrj-73x7
CVE: CVE-2023-39154
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-26
Source: https://github.com/advisories/GHSA-8wgf-3mrj-73x7
Type: github-advisory

## Affected
- Maven: `com.qualys.plugins:qualys-was` — affected >=0 <2.0.11

## Details
Qualys Web App Scanning Connector Plugin 2.0.10 and earlier does not correctly perform permission checks in several HTTP endpoints.

This allows attackers with global Item/Configure permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Qualys Web App Scanning Connector Plugin 2.0.11 requires the appropriate permissions for the affected HTTP endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39154
- https://www.jenkins.io/security/advisory/2023-07-26/#SECURITY-3012
- http://www.openwall.com/lists/oss-security/2023/07/26/2
