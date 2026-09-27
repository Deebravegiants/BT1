# [M] Jenkins GitLab Logo Plugin stores credentials unencrypted

## Summary
Severity: Medium
Advisory: GHSA-22rj-q66g-2jg3
CVE: CVE-2019-10429
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-22rj-q66g-2jg3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gitlab-logo` — affected >=0 <1.0.4

## Details
Jenkins GitLab Logo Plugin stores credentials unencrypted in its global configuration file on the Jenkins master where they can be viewed by users with access to the master file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10429
- https://github.com/jenkinsci/gitlab-logo-plugin/commit/1a64595353df91b5fcf2d9336fa627e06ef1f8a9
- https://github.com/jenkinsci/gitlab-logo-plugin
- https://jenkins.io/security/advisory/2019-09-25/#SECURITY-1575
- http://www.openwall.com/lists/oss-security/2019/09/25/3
