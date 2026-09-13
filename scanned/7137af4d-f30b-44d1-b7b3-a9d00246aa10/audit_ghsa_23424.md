# [H] OS command injection vulnerability in Jenkins Play Framework Plugin

## Summary
Severity: High
Advisory: GHSA-h5mv-fv98-gqmq
CVE: CVE-2020-2200
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h5mv-fv98-gqmq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:play-autotest-plugin` — affected >=0

## Details
A form validation endpoint in Play Framework Plugin executes the `play` command to validate a given input file.

Play Framework Plugin 1.0.2 and earlier lets users specify the path to the `play` command on the Jenkins controller. This results in an OS command injection vulnerability exploitable by users able to store such a file on the Jenkins controller (e.g. through archiving artifacts).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2200
- https://github.com/jenkinsci/play-plugin
- https://jenkins.io/security/advisory/2020-06-03/#SECURITY-1879
- http://www.openwall.com/lists/oss-security/2020/06/03/3
