# [M] Jenkins Kubernetes CI/CD Plugin vulnerable to Improper Authorization

## Summary
Severity: Medium
Advisory: GHSA-hch9-6qrj-5f49
CVE: CVE-2019-10469
CWE: CWE-276, CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hch9-6qrj-5f49
Type: github-advisory

## Affected
- Maven: `com.elasticbox.jenkins-ci.plugins:kubernetes-ci` — affected >=0

## Details
A missing permission check in Jenkins ElasticBox Jenkins Kubernetes CI/CD Plugin allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## Note: Jenkins has suspended distribution of this plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10469
- https://github.com/jenkinsci/kubernetes-ci-plugin
- https://jenkins.io/security/advisory/2019-10-23/#SECURITY-1005%20(1)
- https://plugins.jenkins.io/kubernetes-ci
- http://www.openwall.com/lists/oss-security/2019/10/23/2
