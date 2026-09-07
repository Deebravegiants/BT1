# [M] Cross-Site Request Forgery in Jenkins Deployment Dashboard Plugin

## Summary
Severity: Medium
Advisory: GHSA-x4g7-5xrm-5wmq
CVE: CVE-2022-34797
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-x4g7-5xrm-5wmq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ec2-deployment-dashboard` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Deployment Dashboard Plugin 1.0.10 and earlier allows attackers to connect to an attacker-specified HTTP URL using attacker-specified credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34797
- https://github.com/jenkinsci/ec2-deployment-dashboard
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2798%20(2)
