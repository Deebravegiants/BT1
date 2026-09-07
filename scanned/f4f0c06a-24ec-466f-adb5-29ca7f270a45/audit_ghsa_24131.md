# [M] Jenkins Alauda DevOps Pipeline Plugin allows attackers with Overall/Read permission to capture credentials stored in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-8rfc-v3vj-j62w
CVE: CVE-2019-16574
CWE: CWE-285, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8rfc-v3vj-j62w
Type: github-advisory

## Affected
- Maven: `com.alauda.jenkins.plugins:alauda-devops-pipeline` — affected >=0

## Details
A missing permission check in Jenkins Alauda DevOps Pipeline Plugin 2.3.2 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16574
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1600
- http://www.openwall.com/lists/oss-security/2019/12/17/1
