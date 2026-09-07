# [M] Jenkins JClouds Plugin missing permission check

## Summary
Severity: Medium
Advisory: GHSA-7wxc-7qrg-rg6w
CVE: CVE-2019-10369
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7wxc-7qrg-rg6w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:jclouds-jenkins` — affected >=0 <2.15

## Details
Jenkins JClouds Plugin did not perform permission checks on a method implementing form validation. This allowed users with Overall/Read access to Jenkins to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Additionally, this form validation method did not require POST requests, resulting in a cross-site request forgery vulnerability.

This form validation method now requires POST requests and Overall/Administer permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10369
- https://jenkins.io/security/advisory/2019-08-07/#SECURITY-1482
- https://lists.apache.org/thread.html/r42b7ff290ed5ec8f27f12c54fff54462ffc4bcf6a5015c37fece94ac%40%3Cnotifications.jclouds.apache.org%3E
- https://lists.apache.org/thread.html/r42b7ff290ed5ec8f27f12c54fff54462ffc4bcf6a5015c37fece94ac@%3Cnotifications.jclouds.apache.org%3E
- https://lists.apache.org/thread.html/r6c4693d03d15391814c647742db49a4d9937fa34573fb66103d57b45%40%3Cnotifications.jclouds.apache.org%3E
- https://lists.apache.org/thread.html/r6c4693d03d15391814c647742db49a4d9937fa34573fb66103d57b45@%3Cnotifications.jclouds.apache.org%3E
- https://lists.apache.org/thread.html/r725e55670dbdd214f3cfdfea255b72a75fa9a4f0c6c9d109b29c7881%40%3Cnotifications.jclouds.apache.org%3E
- https://lists.apache.org/thread.html/r725e55670dbdd214f3cfdfea255b72a75fa9a4f0c6c9d109b29c7881@%3Cnotifications.jclouds.apache.org%3E
- http://www.openwall.com/lists/oss-security/2019/08/07/1
