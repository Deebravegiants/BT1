# [M] Jenkins Rundeck Plugin CSRF vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4c2w-wcw4-8jv9
CVE: CVE-2019-10454
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4c2w-wcw4-8jv9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:rundeck` — affected >=0 <3.6.6

## Details
Jenkins Rundeck Plugin does not perform permission checks on a method implementing form validation. This allows users with Overall/Read access to Jenkins to initiate a connection test to an attacker-specified server with attacker-specified username and password.

Additionally, the form validation method does not require POST requests, resulting in a CSRF vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10454
- https://github.com/jenkinsci/rundeck-plugin/commit/68177fc53f40d038233c9d54f3d59fdee9d6ced0
- https://jenkins.io/security/advisory/2019-10-16/#SECURITY-1460
