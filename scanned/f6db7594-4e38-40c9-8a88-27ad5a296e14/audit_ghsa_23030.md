# [M] Jenkins GitHub Branch Source Plugin vulnerable to Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-9cfq-v2hm-c3xr
CVE: CVE-2018-1000185
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-9cfq-v2hm-c3xr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:github-branch-source` — affected >=0 <2.3.5

## Details
A server-side request forgery vulnerability exists in Jenkins GitHub Branch Source Plugin 2.3.4 and older in Endpoint.java that allows attackers with Overall/Read access to cause Jenkins to send a GET request to a specified URL. Additionally, this form validation method did not require POST requests, resulting in a CSRF vulnerability. As of version 23.5, this form validation method requires POST requests and the Overall/Administer permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000185
- https://github.com/jenkinsci/github-branch-source-plugin/commit/22d3383002274bc3f4368534eba2b5c852e78b39
- https://github.com/jenkinsci/github-branch-source-plugin
- https://jenkins.io/security/advisory/2018-06-04/#SECURITY-806
