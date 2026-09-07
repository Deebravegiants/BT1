# [H] Jenkins GitLab Plugin missing permission checks

## Summary
Severity: High
Advisory: GHSA-923w-9p3x-hmgw
CVE: CVE-2019-10301
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-923w-9p3x-hmgw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gitlab-plugin` — affected >=0 <1.5.12

## Details
Jenkins GitLab Plugin did not perform permission checks on a method implementing form validation. This allowed users with Overall/Read access to Jenkins to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.

Additionally, this form validation method did not require POST requests, resulting in a cross-site request forgery vulnerability.

This form validation method now requires POST requests and Overall/Administer permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10301
- https://github.com/jenkinsci/gitlab-plugin/commit/f028c65539a8892f2d1f738cacc1ea5830adf5d3
- https://jenkins.io/security/advisory/2019-04-17/#SECURITY-1357
- https://web.archive.org/web/20200227075952/http://www.securityfocus.com/bid/108045
