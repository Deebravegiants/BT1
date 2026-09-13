# [M] Missing permission check in Jenkins PaaSLane Estimate Plugin

## Summary
Severity: Medium
Advisory: GHSA-jqr2-7f24-xrgc
CVE: CVE-2023-50779
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-jqr2-7f24-xrgc
Type: github-advisory

## Affected
- Maven: `com.cloudtp.jenkins:paaslane-estimate` — affected >=0

## Details
PaaSLane Estimate Plugin 1.0.4 and earlier does not perform permission checks in several HTTP endpoints. This allows attackers with Overall/Read permission to connect to an attacker-specified URL using an attacker-specified token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50779
- https://github.com/jenkinsci/paaslane-plugin
- https://www.jenkins.io/security/advisory/2023-12-13/#SECURITY-3179
- http://www.openwall.com/lists/oss-security/2023/12/13/4
