# [H] Jenkins Kubernetes CI/CD Plugin vulnerable to Cross-Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-vx6r-w45x-q3h6
CVE: CVE-2019-10468
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vx6r-w45x-q3h6
Type: github-advisory

## Affected
- Maven: `com.elasticbox.jenkins-ci.plugins:kubernetes-ci` — affected >=0

## Details
A cross-site request forgery vulnerability in Jenkins ElasticBox Jenkins Kubernetes CI/CD Plugin allows attackers to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins. 

## Note: Jenkins has suspended distribution of this plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10468
- https://github.com/jenkinsci/kubernetes-ci-plugin
- https://jenkins.io/security/advisory/2019-10-23/#SECURITY-1005%20(1)
- https://plugins.jenkins.io/kubernetes-ci
- http://www.openwall.com/lists/oss-security/2019/10/23/2
