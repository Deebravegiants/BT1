# [M] Missing permission check in Jenkins Gerrit Trigger Plugin

## Summary
Severity: Medium
Advisory: GHSA-4r39-f4rh-j6q8
CVE: CVE-2019-16552
CWE: CWE-276, CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4r39-f4rh-j6q8
Type: github-advisory

## Affected
- Maven: `com.sonyericsson.hudson.plugins.gerrit:gerrit-trigger` — affected >=0 <2.30.2

## Details
A missing permission check in Jenkins Gerrit Trigger Plugin 2.30.1 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified HTTP URL or SSH server using attacker-specified credentials, or determine the existence of a file with a given path on the Jenkins master.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16552
- https://github.com/jenkinsci/gerrit-trigger-plugin/commit/bdc94d3e23df0ad6a64565c732498f89ff743b51
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1527
- http://www.openwall.com/lists/oss-security/2019/12/17/1
