# [M] Secret stored in plain text by Jenkins Slack Upload Plugin

## Summary
Severity: Medium
Advisory: GHSA-656g-hf8v-x2rw
CVE: CVE-2020-2208
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-656g-hf8v-x2rw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:slack-uploader` — affected >=0

## Details
Jenkins Slack Upload Plugin 1.7 and earlier stores a secret unencrypted in job `config.xml` files on the Jenkins master where it can be viewed by users with Extended Read permission, or access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2208
- https://github.com/jenkinsci/slack-uploader-plugin
- https://jenkins.io/security/advisory/2020-07-02/#SECURITY-1627
- http://www.openwall.com/lists/oss-security/2020/07/02/7
