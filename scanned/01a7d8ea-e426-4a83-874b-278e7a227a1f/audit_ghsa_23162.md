# [H] Jenkins Ansible Tower Plugin missing permission check

## Summary
Severity: High
Advisory: GHSA-pc24-753j-gmqf
CVE: CVE-2019-10311
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pc24-753j-gmqf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:ansible-tower` — affected >=0 <0.9.2

## Details
Jenkins Ansible Tower Plugin did not perform permission checks on a method implementing form validation. This allowed users with Overall/Read access to Jenkins to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Additionally, this form validation method did not require POST requests, resulting in a cross-site request forgery vulnerability.

This form validation method now requires POST requests and Overall/Administer permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10311
- https://web.archive.org/web/20200227073756/http://www.securityfocus.com/bid/108159
- https://www.jenkins.io/security/advisory/2019-04-30/#SECURITY-1355%20(1)
- http://www.openwall.com/lists/oss-security/2019/04/30/5
