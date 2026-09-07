# [H] Cross-site Scripting in Jenkins eXtreme Feedback Panel Plugin

## Summary
Severity: High
Advisory: GHSA-w257-f7qj-4vrq
CVE: CVE-2022-34790
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-w257-f7qj-4vrq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:xfpanel` — affected >=0

## Details
Jenkins eXtreme Feedback Panel Plugin 2.0.1 and earlier does not escape the job names used in tooltips, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34790
- https://github.com/jenkinsci/xfpanel-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-1939
