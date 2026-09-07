# [M] Stored XSS vulnerability in Jenkins Scriptler Plugin

## Summary
Severity: Medium
Advisory: GHSA-p479-rwhp-rwjx
CVE: CVE-2021-21667
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-p479-rwhp-rwjx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:scriptler` — affected >=0 <3.3

## Details
Jenkins Scriptler Plugin 3.2 and earlier does not escape parameter names shown in job configuration forms.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Scriptler/Configure permission.

Jenkins Scriptler Plugin 3.3 escapes parameter names shown in job configuration forms.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21667
- https://github.com/jenkinsci/scriptler-plugin/commit/ea9c4e6abdd15ee4731e76bb7130069af6dfed88
- https://github.com/jenkinsci/scriptler-plugin
- https://www.jenkins.io/security/advisory/2021-06-16/#SECURITY-2224
- http://www.openwall.com/lists/oss-security/2021/06/16/3
