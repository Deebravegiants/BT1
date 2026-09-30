# [H] System command execution vulnerability in Selection tasks Jenkins Plugin

## Summary
Severity: High
Advisory: GHSA-79h8-7735-v3f9
CVE: CVE-2020-2276
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-79h8-7735-v3f9
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:selection-tasks-plugin` — affected >=0

## Details
Jenkins Selection tasks Plugin 1.0 and earlier executes a user-specified program on the Jenkins controller, allowing attackers with Job/Configure permission to execute an arbitrary system command on the Jenkins controller as the OS user that the Jenkins process is running as.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2276
- https://github.com/jenkinsci/selection-tasks-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1967
- http://www.openwall.com/lists/oss-security/2020/09/16/3
