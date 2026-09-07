# [M] Missing permission checks in Jenkins Amazon EC2 Plugin

## Summary
Severity: Medium
Advisory: GHSA-6hmm-77r2-h6hr
CVE: CVE-2020-2091
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6hmm-77r2-h6hr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ec2` — affected >=0 <1.48

## Details
Amazon EC2 Plugin 1.47 and earlier does not perform permission checks in methods performing form validation. This allows users with Overall/Read access to Jenkins to connect to an attacker-specified URL within the AWS region using attacker-specified credentials IDs obtained through another method.

This vulnerability might also allow attackers to capture credentials stored in Jenkins. We have not been able to confirm that this is possible.

Additionally, these form validation methods do not require POST requests, resulting in a CSRF vulnerability.

Amazon EC2 Plugin 1.48 requires POST requests and Overall/Administer permission for the affected form validation methods.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2091
- https://github.com/jenkinsci/ec2-plugin/commit/0cdbaf2d7da5c368209f427559c8608dec22a63b
- https://github.com/jenkinsci/ec2-plugin
- https://jenkins.io/security/advisory/2020-01-15/#SECURITY-1004
