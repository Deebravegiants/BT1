# [H] Improper Restriction of XML External Entity Reference in Jenkins Chef Sinatra

## Summary
Severity: High
Advisory: GHSA-38w8-h222-wrpp
CVE: CVE-2022-25209
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-38w8-h222-wrpp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:sinatra-chef-builder` — affected >=0

## Details
Chef Sinatra Plugin 1.20 and earlier does not perform a permission check in a method implementing form validation.

As the plugin does not configure its XML parser to prevent XML external entity (XXE) attacks, attackers can have Jenkins parse a crafted XML response that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25209
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-1377
