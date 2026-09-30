# [M] Path traversal vulnerability in Jenkins Publish Over SSH Plugin

## Summary
Severity: Medium
Advisory: GHSA-j8rg-4hjm-8r95
CVE: CVE-2022-23113
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-j8rg-4hjm-8r95
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:publish-over-ssh` — affected >=0 <1.23

## Details
Jenkins Publish Over SSH Plugin 1.22 and earlier performs a validation of the file name specifying whether it is present or not, resulting in a path traversal vulnerability allowing attackers with Item/Configure permission to discover the name of the Jenkins controller files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23113
- https://github.com/jenkinsci/publish-over-ssh-plugin/commit/79f6598a17279125c476a29b21439ad3bd01e6c5
- https://github.com/jenkinsci/publish-over-ssh-plugin
- https://github.com/jenkinsci/publish-over-ssh-plugin/releases/tag/publish-over-ssh-1.23
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-2307
- http://www.openwall.com/lists/oss-security/2022/01/12/6
