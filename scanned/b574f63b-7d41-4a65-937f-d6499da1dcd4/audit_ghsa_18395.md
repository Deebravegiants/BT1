# [M] Jenkins Applitools Eyes Plugin vulnerability exposes unencrypted keys to certain authenticated users

## Summary
Severity: Medium
Advisory: GHSA-q92v-3f4w-5xg8
CVE: CVE-2025-53742
CWE: CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-q92v-3f4w-5xg8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:applitools-eyes` — affected >=0

## Details
Jenkins Applitools Eyes Plugin 1.16.5 and earlier stores Applitools API keys unencrypted in job config.xml files on the Jenkins controller, where they can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53742
- https://github.com/jenkinsci/applitools-eyes-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3510
- http://www.openwall.com/lists/oss-security/2025/07/09/4
