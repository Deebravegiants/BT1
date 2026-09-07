# [M] Improper Neutralization of Input During Web Page Generation in Jenkins Git Plugin 

## Summary
Severity: Medium
Advisory: GHSA-6c7r-6p5m-cp82
CVE: CVE-2020-2136
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6c7r-6p5m-cp82
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:git` — affected >=0 <4.2.1

## Details
Jenkins Git Plugin 4.2.0 and earlier does not escape the error message for the repository URL for Microsoft TFS field form validation, resulting in a stored cross-site scripting vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2136
- https://github.com/jenkinsci/git-plugin/commit/f581998be38cfed8e080c672c4b7caa8b4a45979
- https://jenkins.io/security/advisory/2020-03-09/#SECURITY-1723
- http://www.openwall.com/lists/oss-security/2020/03/09/1
