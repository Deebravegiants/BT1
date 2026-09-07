# [H] Stored XSS vulnerability in Jenkins Git Parameter Plugin

## Summary
Severity: High
Advisory: GHSA-j7q2-c6r4-x2jw
CVE: CVE-2020-2238
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j7q2-c6r4-x2jw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.tools:git-parameter` — affected >=0 <0.9.13

## Details
Jenkins Git Parameter Plugin 0.9.12 and earlier does not escape the repository field on the 'Build with Parameters' page, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Job/Configure permission.

Git Parameter Plugin 0.9.13 escapes the repository field on the 'Build with Parameters' page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2238
- https://github.com/jenkinsci/git-parameter-plugin/commit/7014c4dd030ee4226b4795137050743a84d67cb0
- https://github.com/jenkinsci/git-parameter-plugin
- https://jenkins.io/security/advisory/2020-09-01/#SECURITY-1884
- http://www.openwall.com/lists/oss-security/2020/09/01/3
