# [H] Jenkins Phabricator Differential Plugin vulnerable to XML external entity (XXE) attacks

## Summary
Severity: High
Advisory: GHSA-w4g6-8xqp-g92m
CVE: CVE-2023-28683
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-04-02
Source: https://github.com/advisories/GHSA-w4g6-8xqp-g92m
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:phabricator-plugin` — affected >=0

## Details
Jenkins Phabricator Differential Plugin 2.1.5 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers able to control coverage report file contents for the `Post to Phabricator` post-build action to have Jenkins parse a crafted XML document that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28683
- https://github.com/jenkinsci/phabricator-plugin
- https://www.jenkins.io/security/advisory/2023-03-21/#SECURITY-2942
