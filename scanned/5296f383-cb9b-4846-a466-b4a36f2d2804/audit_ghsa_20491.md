# [M] CSRF vulnerability in Jenkins batch task Plugin

## Summary
Severity: Medium
Advisory: GHSA-mh8g-8jwp-q6xw
CVE: CVE-2022-23115
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-mh8g-8jwp-q6xw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:batch-task` — affected >=0

## Details
Cross-site request forgery (CSRF) vulnerabilities in Jenkins batch task Plugin 1.19 and earlier allows attackers with Overall/Read access to retrieve logs, build or delete a batch task.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23115
- https://github.com/jenkinsci/batch-task-plugin/commit/0e461e230b40d8eeae6e2dfbf00ba7b461ddb0a9
- https://github.com/jenkinsci/batch-task-plugin
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-1025
- http://www.openwall.com/lists/oss-security/2022/01/12/6
