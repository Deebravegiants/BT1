# [M] Path traversal vulnerability on Windows in Jenkins Continuous Integration with Toad Edge Plugin

## Summary
Severity: Medium
Advisory: GHSA-mc92-c859-jr66
CVE: CVE-2022-28148
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-mc92-c859-jr66
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ci-with-toad-edge` — affected >=0 <2.4

## Details
The file browser in Jenkins Continuous Integration with Toad Edge Plugin 2.3 and earlier may interpret some paths to files as absolute on Windows, resulting in a path traversal vulnerability allowing attackers with Item/Read permission to obtain the contents of arbitrary files on Windows controllers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28148
- https://github.com/jenkinsci/ci-with-toad-edge-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2654
- http://www.openwall.com/lists/oss-security/2022/03/29/1
