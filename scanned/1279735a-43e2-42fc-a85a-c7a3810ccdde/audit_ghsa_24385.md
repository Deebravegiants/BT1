# [H] CSRF vulnerability in Email Extension Template Plugin 

## Summary
Severity: High
Advisory: GHSA-4m38-gqh8-x266
CVE: CVE-2018-1000417
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-4m38-gqh8-x266
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:email-ext` — affected >=0 <1.1

## Details
A cross-site request forgery vulnerability exists in Jenkins Email Extension Template Plugin 1.0 and earlier in ExtEmailTemplateManagement.java that allows creating or removing templates.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000417
- https://github.com/jenkinsci/emailext-template-plugin/commit/74653060cef7507425642841e0f2e58d10aa389f
- https://jenkins.io/security/advisory/2018-09-25/#SECURITY-1125
- http://www.securityfocus.com/bid/106532
