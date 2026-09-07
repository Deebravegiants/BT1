# [M] Jenkins Applitools Eyes Plugin vulnerability does not mask API keys on its job configuration form

## Summary
Severity: Medium
Advisory: GHSA-jmrv-rxgr-phvr
CVE: CVE-2025-53743
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-jmrv-rxgr-phvr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:applitools-eyes` — affected >=0

## Details
Jenkins Applitools Eyes Plugin 1.16.5 and earlier does not mask Applitools API keys displayed on the job configuration form, increasing the potential for attackers to observe and capture them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53743
- https://github.com/jenkinsci/applitools-eyes-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3510
- http://www.openwall.com/lists/oss-security/2025/07/09/4
