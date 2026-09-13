# [M] Missing Authorization in Jenkins Deployment Dashboard Plugin

## Summary
Severity: Medium
Advisory: GHSA-q4mr-j6w9-r2mr
CVE: CVE-2022-34798
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-q4mr-j6w9-r2mr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ec2-deployment-dashboard` — affected >=0

## Details
Jenkins Deployment Dashboard Plugin version 1.0.10 and earlier does not perform a permission check in several HTTP endpoints, allowing attackers with Overall/Read permission to connect to an attacker-specified HTTP URL using attacker-specified credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34798
- https://github.com/jenkinsci/ec2-deployment-dashboard
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2798%20(2)
