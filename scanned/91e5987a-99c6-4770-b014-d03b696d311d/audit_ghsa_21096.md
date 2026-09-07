# [H] Cross-Site Request Forgery in Jenkins Recipe Plugin

## Summary
Severity: High
Advisory: GHSA-hv54-cc8f-42jq
CVE: CVE-2022-34792
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-hv54-cc8f-42jq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:recipe` — affected >=0

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Recipe Plugin 1.2 and earlier allows attackers to send an HTTP request to an attacker-specified URL and parse the response as XML.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34792
- https://github.com/jenkinsci/recipe-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2000
