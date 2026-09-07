# [M] Jenkins Log Parser Plugin vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-xqqw-cqjp-52xm
CVE: CVE-2019-10410
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xqqw-cqjp-52xm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:log-parser` — affected >=0 <2.1

## Details
Log Parser Plugin did not escape an error message shown when log parsing patterns are invalid. This resulted in a persisted cross-site scripting vulnerability exploitable by attackers able to control the log parsing rules configuration, typically users with Job/Configure permission.

Jenkins applies the missing escaping by default since 2.146 and LTS 2.138.2, so newer Jenkins releases are not affected by this vulnerability.

Log Parser Plugin version 2.1 escapes all variables displayed in its views.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10410
- https://github.com/jenkinsci/log-parser-plugin
- https://jenkins.io/security/advisory/2019-09-25/#SECURITY-732
- http://www.openwall.com/lists/oss-security/2019/09/25/3
