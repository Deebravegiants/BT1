# [M] Password stored in plain text by Jenkins TestComplete support Plugin

## Summary
Severity: Medium
Advisory: GHSA-r32r-f6wr-cc3w
CVE: CVE-2020-2209
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r32r-f6wr-cc3w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:TestComplete` — affected >=0 <2.5.2

## Details
Jenkins TestComplete support Plugin prior to version 2.5.2 stores a password unencrypted in job `config.xml` files on the Jenkins master where it can be viewed by users with Extended Read permission, or access to the master file system. Version 2.5.2 contains a patch for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2209
- https://github.com/jenkinsci/testcomplete-plugin/commit/00988873c6ea7e8d081380e4262538960efd6bf1
- https://github.com/jenkinsci/testcomplete-plugin/commit/91dae11421b70a334d2058286e30402cf2f86d4b
- https://github.com/jenkinsci/testcomplete-plugin/commit/ca783d3b6be28b13f82865afa6a8888795d57d10
- https://github.com/jenkinsci/testcomplete-plugin
- https://jenkins.io/security/advisory/2020-07-02/#SECURITY-1686
- http://www.openwall.com/lists/oss-security/2020/07/02/7
