# [M] Jenkins DingTalk Plugin Unconditionally Disables SSL/TLS Certificate and Hostname Validation

## Summary
Severity: Medium
Advisory: GHSA-cp9r-g575-xc5f
CVE: CVE-2025-47888
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-05-14
Source: https://github.com/advisories/GHSA-cp9r-g575-xc5f
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:dingding-notifications` — affected >=0

## Details
Jenkins DingTalk Plugin 2.7.3 and earlier unconditionally disables SSL/TLS certificate and hostname validation for connections to the configured DingTalk webhooks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-47888
- https://github.com/jenkinsci/dingtalk-plugin
- https://www.jenkins.io/security/advisory/2025-05-14/#SECURITY-3353
