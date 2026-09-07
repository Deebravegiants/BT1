# [M] Stored Cross-site Scripting vulnerability in Jenkins Tests Selector Plugin

## Summary
Severity: Medium
Advisory: GHSA-q787-qgw2-j2qf
CVE: CVE-2022-28159
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-q787-qgw2-j2qf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:selected-tests-executor` — affected >=0

## Details
Jenkins Tests Selector Plugin 1.3.3 and earlier does not escape the Properties File Path option for Choosing Tests parameters, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28159
- https://github.com/jenkinsci/selected-tests-executor-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2262
- http://www.openwall.com/lists/oss-security/2022/03/29/1
