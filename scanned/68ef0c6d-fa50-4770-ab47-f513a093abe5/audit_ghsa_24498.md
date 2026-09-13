# [H] XXE vulnerability in Jenkins CVS Plugin

## Summary
Severity: High
Advisory: GHSA-g9hg-x9c9-7xgr
CVE: CVE-2020-2324
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g9hg-x9c9-7xgr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:cvs` — affected >=0 <2.17

## Details
Jenkins CVS Plugin 2.16 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks.

This allows attackers able to control an agent process to have Jenkins parse a crafted changelog file that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

Jenkins CVS Plugin 2.17 disables external entity resolution for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2324
- https://github.com/jenkinsci/cvs-plugin/commit/ff121443b282c8dbd6a5ee4841f152f78e4a5954
- https://github.com/jenkinsci/cvs-plugin
- https://www.jenkins.io/security/advisory/2020-12-03/#SECURITY-2146
- http://www.openwall.com/lists/oss-security/2020/12/03/2
