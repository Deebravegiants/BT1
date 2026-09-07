# [M] Cross-site request forgery in Jenkins Gerrit Trigger Plugin

## Summary
Severity: Medium
Advisory: GHSA-95jq-24cr-pgrq
CVE: CVE-2023-24423
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-95jq-24cr-pgrq
Type: github-advisory

## Affected
- Maven: `com.sonyericsson.hudson.plugins.gerrit:gerrit-trigger` — affected >=0 <2.38.1

## Details
A cross-site request forgery (CSRF) vulnerability in Jenkins Gerrit Trigger Plugin 2.38.0 and earlier allows attackers to rebuild previous builds triggered by Gerrit.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24423
- https://github.com/jenkinsci/gerrit-trigger-plugin/commit/691d76fdf54d659f8585ea3cbc3cce60d9edfec8
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2137
