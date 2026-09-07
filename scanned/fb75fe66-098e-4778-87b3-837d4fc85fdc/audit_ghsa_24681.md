# [M] Loop with Unreachable Exit Condition in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-9cjv-93g7-c6mv
CVE: CVE-2018-1000864
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-9cjv-93g7-c6mv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.138.4
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.140 <2.154

## Details
A denial of service vulnerability exists in Jenkins 2.153 and earlier, LTS 2.138.3 and earlier in CronTab.java that allows attackers with Overall/Read permission to have a request handling thread enter an infinite loop.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000864
- https://github.com/jenkinsci/jenkins/commit/73afa0ca786a87f05b5433e2e38f863826fcad17
- https://access.redhat.com/errata/RHBA-2019:0024
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2018-12-05/#SECURITY-1193
- http://www.securityfocus.com/bid/106176
