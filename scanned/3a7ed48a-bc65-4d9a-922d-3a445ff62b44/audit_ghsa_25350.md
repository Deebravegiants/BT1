# [H] Stored XSS vulnerability in Jenkins Matrix Authorization Strategy Plugin

## Summary
Severity: High
Advisory: GHSA-vr6v-wjfw-rxcr
CVE: CVE-2020-2226
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vr6v-wjfw-rxcr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:matrix-auth` — affected >=0 <2.6.2

## Details
Matrix Authorization Strategy Plugin 2.6.1 and earlier does not escape user names shown in the permission table. This results in a stored cross-site scripting (XSS) vulnerability. When using project-based matrix authorization, this vulnerability can be exploited by a user with Job/Configure or Agent/Configure permission, otherwise by users with Overall/Administer permission.

Matrix Authorization Strategy Plugin 2.6.2 escapes user names in the permission table.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2226
- https://github.com/jenkinsci/matrix-auth-plugin/commit/e263a2feb47594787952a7e0bd1550e849c58b07
- https://github.com/jenkinsci/matrix-auth-plugin
- https://jenkins.io/security/advisory/2020-07-15/#SECURITY-1909
- http://www.openwall.com/lists/oss-security/2020/07/15/5
