# [M] Jenkins MQ Notifier Plugin exposes sensitive information in build logs

## Summary
Severity: Medium
Advisory: GHSA-8fm4-r23p-v68v
CVE: CVE-2024-28154
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-8fm4-r23p-v68v
Type: github-advisory

## Affected
- Maven: `com.sonymobile.jenkins.plugins.mq:mq-notifier` — affected >=0 <1.4.1

## Details
Jenkins MQ Notifier Plugin 1.4.0 and earlier logs potentially sensitive build parameters as part of debug information in build logs by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28154
- https://github.com/jenkinsci/mq-notifier-plugin/commit/46c9f228a3317eb87562bc3d99f7e184bdcecbfe
- https://github.com/jenkinsci/mq-notifier-plugin
- https://www.jenkins.io/security/advisory/2024-03-06/#SECURITY-3180
- http://www.openwall.com/lists/oss-security/2024/03/06/3
