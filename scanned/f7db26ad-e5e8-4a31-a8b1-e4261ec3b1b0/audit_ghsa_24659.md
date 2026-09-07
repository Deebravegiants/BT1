# [M] Stored XSS vulnerability in Jenkins Timestamper Plugin

## Summary
Severity: Medium
Advisory: GHSA-6xxf-rwv4-mrjm
CVE: CVE-2020-2137
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6xxf-rwv4-mrjm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:timestamper` — affected >=0 <1.11.2

## Details
Timestamper Plugin 1.11.1 and earlier does not escape or sanitize the HTML formatting used to display the timestamps in console output for builds.

This results in a stored cross-site scripting vulnerability that can be exploited by users with Overall/Administer permission.

Timestamper Plugin 1.11.2 sanitizes the HTML formatting for timestamps and only allows basic, safe HTML formatting.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2137
- https://github.com/jenkinsci/timestamper-plugin/commit/6637c3e599c330e03251005675beeadb46d8495b
- https://github.com/jenkinsci/timestamper-plugin
- https://jenkins.io/security/advisory/2020-03-09/#SECURITY-1784
- http://www.openwall.com/lists/oss-security/2020/03/09/1
