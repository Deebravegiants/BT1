# [H] CSRF vulnerability in Jenkins Role-based Authorization Strategy Plugin configuration

## Summary
Severity: High
Advisory: GHSA-774g-r3fm-4v85
CVE: CVE-2017-1000090
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-774g-r3fm-4v85
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:role-strategy` — affected >=0 <2.5.1

## Details
Role-based Authorization Strategy Plugin was not requiring requests to its API be sent via POST, thereby opening itself to Cross-Site Request Forgery attacks. This allowed attackers to add administrator role to any user, or to remove the authorization configuration, preventing legitimate access to Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000090
- https://jenkins.io/security/advisory/2017-07-10
