# [H] Cross site scripting in Jenkins build-metrics Plugin

## Summary
Severity: High
Advisory: GHSA-j2gv-q44j-xm42
CVE: CVE-2022-34784
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-j2gv-q44j-xm42
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:build-metrics` — affected >=0

## Details
Jenkins build-metrics Plugin 1.3 does not escape the build description on one of its views, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Build/Update permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34784
- https://github.com/jenkinsci/build-metrics-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-1118
