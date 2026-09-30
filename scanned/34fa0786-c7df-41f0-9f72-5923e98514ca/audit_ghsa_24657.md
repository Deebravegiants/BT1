# [H] Incorrect Authorization in Jenkins Script Security Plugin

## Summary
Severity: High
Advisory: GHSA-62pm-mgrh-7p69
CVE: CVE-2019-16538
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-62pm-mgrh-7p69
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1.68

## Details
A sandbox bypass vulnerability in Jenkins Script Security Plugin 1.67 and earlier related to the handling of default parameter expressions in closures allowed attackers to execute arbitrary code in sandboxed scripts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16538
- https://github.com/jenkinsci/script-security-plugin/commit/0e7da14171ed1d03ff72f6910392e630b40a8590
- https://jenkins.io/security/advisory/2019-11-21/#SECURITY-1658
- http://www.openwall.com/lists/oss-security/2019/11/21/1
