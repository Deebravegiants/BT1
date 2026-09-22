# [H] XXE vulnerability in Jenkins REPO Plugin

## Summary
Severity: High
Advisory: GHSA-2w2m-ccf8-57cq
CVE: CVE-2022-43415
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-2w2m-ccf8-57cq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:repo` — affected >=0 <1.16.0

## Details
REPO Plugin 1.15.0 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers able to control which `repo` binary is executed on agents to have Jenkins parse a crafted XML document that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

REPO Plugin 1.16.0 disables external entity resolution for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43415
- https://github.com/jenkinsci/repo-plugin/commit/4c4a72c7de3d3e5bbbad223605ea264dcec56bc1
- https://github.com/jenkinsci/repo-plugin
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2337
- http://www.openwall.com/lists/oss-security/2022/10/19/3
