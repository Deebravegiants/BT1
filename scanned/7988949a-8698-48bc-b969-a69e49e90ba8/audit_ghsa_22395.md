# [M] Incorrect default pattern in Jenkins Audit Trail Plugin

## Summary
Severity: Medium
Advisory: GHSA-7v9p-34r2-q668
CVE: CVE-2020-2288
CWE: CWE-185
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7v9p-34r2-q668
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:audit-trail` — affected >=0 <3.7

## Details
Jenkins Audit Trail Plugin uses regular expressions to match requested URLs whose dispatch should be logged.

In Jenkins Audit Trail Plugin 3.6 and earlier, the default regular expression pattern could be bypassed in many cases by adding a suffix to the URL that would be ignored during request handling.

Jenkins Audit Trail Plugin 3.7 changes the default regular expression pattern so that it allows for arbitrary suffixes. It automatically will replace previous default patterns with the new, more complete default pattern.

Additionally, an administrative monitor is shown if a user-specified pattern is found to be bypassable through crafted URLs and form validation was improved to recognize patterns that would not match requests with arbitrary suffixes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2288
- https://github.com/jenkinsci/audit-trail-plugin/commit/43433147bec001f13536534d3d282ce3c28b26be
- https://github.com/jenkinsci/audit-trail-plugin
- https://www.jenkins.io/security/advisory/2020-10-08/#SECURITY-1846
- http://www.openwall.com/lists/oss-security/2020/10/08/5
