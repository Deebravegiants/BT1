# [M] Jenkins CAS Plugin Server-Side Request Forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-f8r7-7hv9-7f43
CVE: CVE-2018-1000188
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-f8r7-7hv9-7f43
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cas-plugin` — affected >=0 <1.4.2

## Details
A server-side request forgery vulnerability exists in Jenkins CAS Plugin 1.4.1 and older in CasSecurityRealm.java that allows attackers with Overall/Read access to cause Jenkins to send a GET request to a specified URL. Additionally, this form validation method did not require POST requests, resulting in a CSRF vulnerability. As of version 1.4.2, this form validation method requires POST requests and the Overall/Administer permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000188
- https://github.com/jenkinsci/cas-plugin/commit/25d952151d61dec3627e875f03ac4f648d5e883d
- https://github.com/jenkinsci/cas-plugin
- https://jenkins.io/security/advisory/2018-06-04/#SECURITY-809
