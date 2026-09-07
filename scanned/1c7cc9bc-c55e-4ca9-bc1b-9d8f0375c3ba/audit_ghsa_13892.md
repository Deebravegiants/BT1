# [M] Cross-site Scripting in Jenkins JUnit Plugin

## Summary
Severity: Medium
Advisory: GHSA-ph74-8rgx-64c5
CVE: CVE-2023-25761
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-15
Source: https://github.com/advisories/GHSA-ph74-8rgx-64c5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:junit` — affected >=0 <1166.1168.vd6b_8042a_06de

## Details
Jenkins JUnit Plugin 1166.va_436e268e972 and earlier does not escape test case class names in JavaScript expressions, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to control test case class names in the JUnit resources processed by the plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25761
- https://github.com/jenkinsci/junit-plugin/commit/d6b8042a06de4aaaf0942ad79036095b853eea02
- https://www.jenkins.io/security/advisory/2023-02-15/#SECURITY-3032
- http://www.openwall.com/lists/oss-security/2023/02/15/4
