# [H] Cross-Site Request Forgery in Jenkins Alauda Kubernetes Suport Plugin

## Summary
Severity: High
Advisory: GHSA-5hvr-3fcr-wx8c
CVE: CVE-2019-16575
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5hvr-3fcr-wx8c
Type: github-advisory

## Affected
- Maven: `io.alauda.jenkins.plugins:alauda-kubernetes-support` — affected >=0

## Details
A cross-site request forgery vulnerability in Jenkins Alauda Kubernetes Suport Plugin 2.3.0 and earlier allows attackers to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing the Kubernetes service account token or credentials stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16575
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1602
- http://www.openwall.com/lists/oss-security/2019/12/17/1
