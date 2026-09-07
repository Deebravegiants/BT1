# [M] Jenkins NS-ND Integration Performance Publisher Plugin vulnerable to Missing Authorization

## Summary
Severity: Medium
Advisory: GHSA-j2mj-g8jp-gjfm
CVE: CVE-2022-41228
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-j2mj-g8jp-gjfm
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:cavisson-ns-nd-integration` — affected >=0 <4.8.0.130

## Details
A missing permission check in Jenkins NS-ND Integration Performance Publisher Plugin 4.8.0.129 and earlier allows attackers with Overall/Read permissions to connect to an attacker-specified webserver using attacker-specified credentials. Version 4.8.0.130 requires POST requests and Overall/Administer permission for the affected form validation method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41228
- https://github.com/jenkinsci/cavisson-ns-nd-integration-plugin
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2737
