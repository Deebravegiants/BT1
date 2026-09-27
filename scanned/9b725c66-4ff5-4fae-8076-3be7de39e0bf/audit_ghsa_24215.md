# [M] Improper Authorization in Jenkins Alauda Kubernetes Suport Plugin

## Summary
Severity: Medium
Advisory: GHSA-7h24-4x4c-69mf
CVE: CVE-2019-16576
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7h24-4x4c-69mf
Type: github-advisory

## Affected
- Maven: `io.alauda.jenkins.plugins:alauda-kubernetes-support` — affected >=0

## Details
A missing permission check in Jenkins Alauda Kubernetes Suport Plugin 2.3.0 and earlier allows attackers with Overall/Read permission to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing the Kubernetes service account token or credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16576
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1602
- http://www.openwall.com/lists/oss-security/2019/12/17/1
