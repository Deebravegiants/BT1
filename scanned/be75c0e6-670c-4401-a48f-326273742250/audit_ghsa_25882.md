# [M] Stored Cross-site Scripting vulnerability in Jenkins List Git Branches Parameter Plugin

## Summary
Severity: Medium
Advisory: GHSA-7756-56hr-2vcp
CVE: CVE-2022-27212
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-7756-56hr-2vcp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:list-git-branches-parameter` — affected >=0

## Details
Jenkins List Git Branches Parameter Plugin 0.0.9 and earlier does not escape the name of the 'List Git branches (and more)' parameter, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27212
- https://github.com/jenkinsci/list-git-branches-parameter-plugin
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-2167
- http://www.openwall.com/lists/oss-security/2022/03/15/2
