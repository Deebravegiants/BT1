# [M] Stored XSS vulnerability in Matrix Project Plugin

## Summary
Severity: Medium
Advisory: GHSA-vqwg-4v6f-h6x5
CVE: CVE-2022-20615
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-vqwg-4v6f-h6x5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:matrix-project` — affected >=1.19 <1.20
- Maven: `org.jenkins-ci.plugins:matrix-project` — affected >=0 <1.18.1

## Details
Jenkins Matrix Project Plugin prior to 1.20 and 1.18.1 does not escape HTML metacharacters in node and label names, and label descriptions.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Agent/Configure permission.

Matrix Project Plugin 1.20 and 1.18.1 escapes HTML metacharacters in node and label names, and label descriptions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-20615
- https://github.com/jenkinsci/matrix-project-plugin/commit/78cc60556304965ffb2dd8c017bf61d4f153f5ea
- https://github.com/CVEProject/cvelist/blob/2d78eb36f4d084db7fb35f1535d8d84fdcb7d859/2022/20xxx/CVE-2022-20615.json
- https://github.com/jenkinsci/matrix-project-plugin
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-2017
- https://www.oracle.com/security-alerts/cpuapr2022.html
- http://www.openwall.com/lists/oss-security/2022/01/12/6
