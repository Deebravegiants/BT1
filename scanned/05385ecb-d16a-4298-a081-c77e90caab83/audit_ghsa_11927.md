# [M] Jenkins LoadNinja Plugin stores LoadNinja API keys unencrypted in job config.xml files

## Summary
Severity: Medium
Advisory: GHSA-qqjr-hf5h-jx3q
CVE: CVE-2026-33003
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-qqjr-hf5h-jx3q
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:loadninja` — affected >=0 <2.2

## Details
Jenkins LoadNinja Plugin 2.1 and earlier stores LoadNinja API keys unencrypted in job config.xml files on the Jenkins controller where they can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33003
- https://github.com/jenkinsci/loadninja-plugin
- https://www.jenkins.io/security/advisory/2026-03-18/#SECURITY-3642
