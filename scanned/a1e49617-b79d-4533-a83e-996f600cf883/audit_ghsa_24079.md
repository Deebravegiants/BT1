# [H] Missing permission checks in Jenkins Sounds Plugin allow OS command execution

## Summary
Severity: High
Advisory: GHSA-h8w6-c53g-53vv
CVE: CVE-2020-2097
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h8w6-c53g-53vv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:sounds` — affected >=0 <0.6

## Details
Jenkins Sounds Plugin 0.5 and earlier does not perform permission checks in URLs performing form validation, allowing attackers with Overall/Read access to execute arbitrary OS commands as the OS user account running Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2097
- https://github.com/jenkinsci/sounds-plugin/commit/0c376d46fd91b12696e5f7389110ddece0724457
- https://jenkins.io/security/advisory/2020-01-15/#SECURITY-814
