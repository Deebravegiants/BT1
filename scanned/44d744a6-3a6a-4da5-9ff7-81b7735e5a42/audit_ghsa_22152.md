# [M] Jenkins JX Resources Plugin missing permission check 

## Summary
Severity: Medium
Advisory: GHSA-xqqr-mq8x-22qx
CVE: CVE-2019-10339
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xqqr-mq8x-22qx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jx-resources` — affected >=0 <1.0.37

## Details
Jenkins jx-resources Plugin did not perform permission checks on a method implementing form validation. This allowed users with Overall/Read access to Jenkins to connect to an attacker-specified Kubernetes server and obtain information about an attacker-specified namespace. Doing so might also leak service account credentials used for the connection. Additionally, it allowed attackers to obtain the value of any attacker-specified environment variable for the Jenkins controller process.

Additionally, this form validation method did not require POST requests, resulting in a cross-site request forgery vulnerability.

This form validation method now requires POST requests and Overall/Administer permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10339
- https://github.com/jenkinsci/jx-resources-plugin/commit/f0d9fb76230b65e851095da936a439d953c5f64d
- https://jenkins.io/security/advisory/2019-06-11/#SECURITY-1379
- https://web.archive.org/web/20200227033720/http://www.securityfocus.com/bid/108747
- http://www.openwall.com/lists/oss-security/2019/06/11/1
