# [M] XXE vulnerability in Jenkins Nerrvana Plugin

## Summary
Severity: Medium
Advisory: GHSA-wcrg-92wp-4h28
CVE: CVE-2020-2298
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wcrg-92wp-4h28
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:nerrvana-plugin` — affected >=0

## Details
Jenkins Nerrvana Plugin 1.02.06 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers with Overall/Read permission to have Jenkins parse a crafted HTTP request with XML data that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

Additionally, XML parsing is exposed as a form validation endpoint that does not require POST requests, allowing exploitation by users without Overall/Read permission via CSRF.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2298
- https://github.com/jenkinsci/nerrvana-plugin
- https://www.jenkins.io/security/advisory/2020-10-08/#SECURITY-2097
- http://www.openwall.com/lists/oss-security/2020/10/08/5
