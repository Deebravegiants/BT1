# [M] Reflected XSS vulnerability in Jenkins Queue cleanup Plugin

## Summary
Severity: Medium
Advisory: GHSA-m7pr-m4cx-6m22
CVE: CVE-2020-2169
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m7pr-m4cx-6m22
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:queue-cleanup` — affected >=0 <1.4

## Details
A form validation HTTP endpoint in Queue cleanup Plugin 1.3 and earlier does not escape a query parameter displayed in an error message. This results in a reflected cross-site scripting vulnerability (XSS).

Queue cleanup Plugin 1.4 correctly escapes the query parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2169
- https://github.com/jenkinsci/queue-cleanup-plugin/commit/b3e562a427e704fc15dafe7664bd67aafcd4e03e
- https://github.com/jenkinsci/queue-cleanup-plugin/commit/e7dae99aa3a414004e953303c7c687d65348de11
- https://github.com/jenkinsci/queue-cleanup-plugin
- https://jenkins.io/security/advisory/2020-03-25/#SECURITY-1724
- http://www.openwall.com/lists/oss-security/2020/03/25/2
