# [H] Jenkins Script Security Plugin allows for Bypass of Groovy Sandbox Protection

## Summary
Severity: High
Advisory: GHSA-xgjx-96v4-mqxx
CVE: CVE-2016-3102
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-xgjx-96v4-mqxx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1.18.1

## Details
The Script Security plugin before 1.18.1 in Jenkins might allow remote attackers to bypass a Groovy sandbox protection mechanism via a plugin that performs (1) direct field access or (2) get/set array operations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3102
- https://github.com/jenkinsci/script-security-plugin/commit/e7d3bc9c1e25caa23cea33381134a4baaedc75b8
- https://github.com/jenkinsci/script-security-plugin
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2016-04-11
