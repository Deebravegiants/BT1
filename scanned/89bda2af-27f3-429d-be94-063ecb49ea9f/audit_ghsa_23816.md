# [M] Arbitrary file read vulnerability in Jenkins Persona Plugin

## Summary
Severity: Medium
Advisory: GHSA-5mfw-p6qv-wgvv
CVE: CVE-2020-2293
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5mfw-p6qv-wgvv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:persona` — affected >=0

## Details
Jenkins Persona Plugin 2.4 and earlier allows users with Overall/Read permission to read arbitrary files on the Jenkins controller.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2293
- https://github.com/jenkinsci/persona-plugin
- https://www.jenkins.io/security/advisory/2020-10-08/#SECURITY-2046
- http://www.openwall.com/lists/oss-security/2020/10/08/5
