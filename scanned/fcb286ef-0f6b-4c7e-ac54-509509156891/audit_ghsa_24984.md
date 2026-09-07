# [M] Server-side request forgery vulnerability in Jenkins Mesos Plugin

## Summary
Severity: Medium
Advisory: GHSA-5q7j-8hpc-4848
CVE: CVE-2018-1000421
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-5q7j-8hpc-4848
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:mesos` — affected >=0 <0.18

## Details
An improper authorization vulnerability exists in Jenkins Mesos Plugin 0.17.1 and earlier in MesosCloud.java that allows attackers with Overall/Read access to initiate a test connection to an attacker-specified Mesos server with attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000421
- https://jenkins.io/security/advisory/2018-09-25/#SECURITY-1013%20(2)
- http://www.securityfocus.com/bid/106532
