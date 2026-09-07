# [H] Arbitrary file read vulnerability in Jenkins Log Command Plugin

## Summary
Severity: High
Advisory: GHSA-qjpf-2jhx-3758
CVE: CVE-2024-23904
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-qjpf-2jhx-3758
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:log-command` — affected >=0

## Details
Jenkins Log Command Plugin 1.0.2 and earlier does not disable a feature of its command parser that replaces an '@' character followed by a file path in an argument with the file's contents, allowing unauthenticated attackers to read content from arbitrary files on the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23904
- https://github.com/jenkinsci/log-command-plugin
- https://www.jenkins.io/security/advisory/2024-01-24/#SECURITY-3334
- http://www.openwall.com/lists/oss-security/2024/01/24/6
