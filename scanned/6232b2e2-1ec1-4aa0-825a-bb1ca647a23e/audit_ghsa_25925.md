# [M] Arbitrary file read vulnerability in Jenkins Tests Selector Plugin

## Summary
Severity: Medium
Advisory: GHSA-3r5x-x6xf-m8fv
CVE: CVE-2022-28160
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-3r5x-x6xf-m8fv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:selected-tests-executor` — affected >=0

## Details
Jenkins Tests Selector Plugin 1.3.3 and earlier allows users with Item/Configure permission to read arbitrary files on the Jenkins controller.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28160
- https://github.com/jenkinsci/selected-tests-executor-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2338
- http://www.openwall.com/lists/oss-security/2022/03/29/1
