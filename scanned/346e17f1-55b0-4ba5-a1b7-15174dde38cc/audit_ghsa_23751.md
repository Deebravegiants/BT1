# [M] Jenkins ElectricFlow Plugin cross-site request forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-76x4-hr82-cg3m
CVE: CVE-2019-10331
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-76x4-hr82-cg3m
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:electricflow` — affected >=0 <1.1.7

## Details
A missing permission check in a form validation method in CloudBees CD Plugin allowed users with Overall/Read permission to initiate a connection test to an attacker-specified server with attacker-specified username and password.

Additionally, the form validation method did not require POST requests, resulting in a CSRF vulnerability.

This form validation method now requires POST requests and Overall/Administer permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10331
- https://jenkins.io/security/advisory/2019-06-11/#SECURITY-1410%20(1)
- https://web.archive.org/web/20200227033720/http://www.securityfocus.com/bid/108747
- http://www.openwall.com/lists/oss-security/2019/06/11/1
