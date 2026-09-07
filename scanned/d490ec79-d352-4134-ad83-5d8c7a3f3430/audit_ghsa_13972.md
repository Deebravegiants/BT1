# [M] Cross-site Scripting in Jenkins Email Extension Plugin

## Summary
Severity: Medium
Advisory: GHSA-h97r-fchm-m23x
CVE: CVE-2023-25763
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-15
Source: https://github.com/advisories/GHSA-h97r-fchm-m23x
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:email-ext` — affected >=0 <2.94

## Details
Jenkins Email Extension Plugin 2.93 and earlier does not escape various fields included in bundled email templates, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to control affected fields.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25763
- https://github.com/jenkinsci/email-ext-plugin/commit/ebfb97475ec6491f28b88a8b5acbb99ff36f4d7f
- https://github.com/jenkinsci/email-ext-plugin
- https://www.jenkins.io/security/advisory/2023-02-15/#SECURITY-2931
- http://www.openwall.com/lists/oss-security/2023/02/15/4
