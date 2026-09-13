# [M] Jenkins LoadNinja Plugin does not mask LoadNinja API keys displayed on the job configuration form

## Summary
Severity: Medium
Advisory: GHSA-p9hg-wrmv-v8cp
CVE: CVE-2026-33004
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-p9hg-wrmv-v8cp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:loadninja` — affected >=0 <2.2

## Details
Jenkins LoadNinja Plugin 2.1 and earlier does not mask LoadNinja API keys displayed on the job configuration form, increasing the potential for attackers to observe and capture them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33004
- https://github.com/jenkinsci/loadninja-plugin
- https://www.jenkins.io/security/advisory/2026-03-18/#SECURITY-3642
