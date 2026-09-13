# [M] Jenkins Kubernetes CI/CD Plugin vulnerable to Credential Enumeration

## Summary
Severity: Medium
Advisory: GHSA-7jf5-p556-75pr
CVE: CVE-2019-10470
CWE: CWE-276, CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7jf5-p556-75pr
Type: github-advisory

## Affected
- Maven: `com.elasticbox.jenkins-ci.plugins:kubernetes-ci` — affected >=0

## Details
A missing permission check in Jenkins ElasticBox Jenkins Kubernetes CI/CD Plugin in form-related methods allowed users with Overall/Read access to enumerate credentials ID of credentials stored in Jenkins.

## Note: Jenkins has suspended distribution of this plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10470
- https://github.com/jenkinsci/kubernetes-ci-plugin
- https://jenkins.io/security/advisory/2019-10-23/#SECURITY-1005%20(2)
- https://plugins.jenkins.io/kubernetes-ci
- http://www.openwall.com/lists/oss-security/2019/10/23/2
