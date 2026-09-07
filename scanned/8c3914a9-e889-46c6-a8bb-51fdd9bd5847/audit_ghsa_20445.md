# [M] CSRF vulnerability and missing permission checks in Jenkins Publish Over SSH Plugin

## Summary
Severity: Medium
Advisory: GHSA-884c-9wwh-9p6v
CVE: CVE-2022-23111
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-884c-9wwh-9p6v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:publish-over-ssh` — affected >=0 <1.23

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Publish Over SSH Plugin 1.22 and earlier allows attackers to connect to an attacker-specified SSH server using attacker-specified credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23111
- https://github.com/jenkinsci/publish-over-ssh-plugin/commit/21bf41adbce9e71d3f77e113e29bf81d437cadc3
- https://github.com/jenkinsci/publish-over-ssh-plugin
- https://github.com/jenkinsci/publish-over-ssh-plugin/releases/tag/publish-over-ssh-1.23
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-2290
- http://www.openwall.com/lists/oss-security/2022/01/12/6
