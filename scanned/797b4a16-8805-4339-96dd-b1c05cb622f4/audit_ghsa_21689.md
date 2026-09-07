# [H] CSRF vulnerability in Jenkins Chef Sinatra Plugin allow XXE

## Summary
Severity: High
Advisory: GHSA-x92v-xv3x-9v29
CVE: CVE-2022-25207
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-x92v-xv3x-9v29
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:sinatra-chef-builder` — affected >=0

## Details
Jenkins Chef Sinatra Plugin 1.20 and earlier does not perform a permission check in a method implementing form validation.

This allows attackers with Overall/Read permission to have Jenkins send an HTTP request to an attacker-controlled URL and have it parse the response as XML.

As the plugin does not configure its XML parser to prevent XML external entity (XXE) attacks, attackers can have Jenkins parse a crafted XML response that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

Additionally, this form validation method does not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25207
- https://github.com/jenkinsci/sinatra-chef-builder-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-1377
- http://www.openwall.com/lists/oss-security/2022/02/15/2
