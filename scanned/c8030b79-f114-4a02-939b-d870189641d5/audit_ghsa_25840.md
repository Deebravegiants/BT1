# [M] Missing permission check in Jenkins Continuous Integration with Toad Edge Plugin

## Summary
Severity: Medium
Advisory: GHSA-8hh2-rxm8-7fj8
CVE: CVE-2022-28147
CWE: CWE-281, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-8hh2-rxm8-7fj8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ci-with-toad-edge` — affected >=0 <2.4

## Details
A missing permission check in Jenkins Continuous Integration with Toad Edge Plugin 2.3 and earlier allows attackers with Overall/Read permission to check for the existence of an attacker-specified file path on the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28147
- https://github.com/jenkinsci/ci-with-toad-edge-plugin/commit/2b65d62ebb71ec727097aa409c623f9c7c3b2792
- https://github.com/jenkinsci/ci-with-toad-edge-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-2635
- http://www.openwall.com/lists/oss-security/2022/03/29/1
