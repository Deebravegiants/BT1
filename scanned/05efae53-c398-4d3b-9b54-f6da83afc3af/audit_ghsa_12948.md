# [H] Jenkins Flaky Test Handler Plugin stored cross-site scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-hv48-hgp6-xpqf
CVE: CVE-2023-40342
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-16
Source: https://github.com/advisories/GHSA-hv48-hgp6-xpqf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:flaky-test-handler` — affected >=0 <1.2.3

## Details
Jenkins Flaky Test Handler Plugin 1.2.2 and earlier does not escape JUnit test contents when showing them on the Jenkins UI.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to control JUnit report file contents.

Flaky Test Handler Plugin 1.2.3 escapes JUnit test contents when showing them on the Jenkins UI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40342
- https://www.jenkins.io/security/advisory/2023-08-16/#SECURITY-3223
- http://www.openwall.com/lists/oss-security/2023/08/16/3
