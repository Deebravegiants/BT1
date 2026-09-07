# [M] Improper Neutralization of Input During Web Page Generation in Jenkins Script Security Plugin

## Summary
Severity: Medium
Advisory: GHSA-q87g-7mp5-765q
CVE: CVE-2020-2190
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q87g-7mp5-765q
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1.73

## Details
Jenkins Script Security Plugin 1.72 and earlier does not correctly escape pending or approved classpath entries on the In-process Script Approval page, resulting in a stored cross-site scripting vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2190
- https://github.com/jenkinsci/script-security-plugin/commit/99e6ac0df5fe0f0cc6c2a695f7c1f845279bedbd
- https://jenkins.io/security/advisory/2020-06-03/#SECURITY-1866
- http://www.openwall.com/lists/oss-security/2020/06/03/3
