# [M] Jenkins XebiaLabs XL Deploy Plugin vulnerable to Cross-site request forgery (CSRF)

## Summary
Severity: Medium
Advisory: GHSA-grpp-gx5h-pvh8
CVE: CVE-2019-10304
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-grpp-gx5h-pvh8
Type: github-advisory

## Affected
- Maven: `com.xebialabs.deployit.ci:deployit-plugin` — affected >=0 <7.5.5

## Details
A missing permission check in a form validation method in Jenkins XebiaLabs XL Deploy Plugin allows users with Overall/Read permission to initiate a connection test to an attacker-specified server with attacker-specified credentials.

Additionally, the form validation method does not require POST requests, resulting in a CSRF vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10304
- https://github.com/jenkinsci/xldeploy-plugin/commit/5acf9d797fe0afb4defa7c1d5e198103fcdb6989
- https://jenkins.io/security/advisory/2019-04-17/#SECURITY-983
- https://web.archive.org/web/20200227075952/http://www.securityfocus.com/bid/108045
