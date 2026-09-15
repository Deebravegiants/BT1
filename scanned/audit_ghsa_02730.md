# [M] XXE vulnerability in Jenkins Selenium HTML report Plugin

## Summary
Severity: Medium
Advisory: GHSA-hxxp-6546-wv6r
CVE: CVE-2021-21672
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-07-02
Source: https://github.com/advisories/GHSA-hxxp-6546-wv6r
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:seleniumhtmlreport` — affected >=0 <1.1

## Details
Jenkins Selenium HTML report Plugin 1.0 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers with the ability to control the report files parsed using this plugin to have Jenkins parse a crafted report file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

Jenkins Selenium HTML report Plugin 1.1 disables external entity resolution for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21672
- https://github.com/jenkinsci/seleniumhtmlreport-plugin/commit/5ca59b8c7d23af4450dc7f19c1b4107d59063ae1
- https://github.com/jenkinsci/seleniumhtmlreport-plugin
- https://www.jenkins.io/security/advisory/2021-06-30/#SECURITY-2329
- http://www.openwall.com/lists/oss-security/2021/06/30/1
- http://www.openwall.com/lists/oss-security/2022/04/14/2
