# [H] Remote Code Execution vulnerability in Jenkins Literate Plugin

## Summary
Severity: High
Advisory: GHSA-c329-r874-xc7j
CVE: CVE-2020-2158
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c329-r874-xc7j
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:literate` — affected >=0

## Details
Jenkins Literate Plugin 1.0 and earlier does not configure its YAML parser to prevent the instantiation of arbitrary types, resulting in a remote code execution vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2158
- https://github.com/jenkinsci/literate-plugin
- https://jenkins.io/security/advisory/2020-03-09/#SECURITY-1750
- http://www.openwall.com/lists/oss-security/2020/03/09/1
