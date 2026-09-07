# [M] Jenkins Warrior Framework Plugin vulnerability exposes unencrypted passwords to certain authenticated users

## Summary
Severity: Medium
Advisory: GHSA-2g8w-9933-36vr
CVE: CVE-2025-53675
CWE: CWE-256
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-2g8w-9933-36vr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:warrior` — affected >=0

## Details
Jenkins Warrior Framework Plugin 1.2 and earlier stores passwords unencrypted in job config.xml files on the Jenkins controller, where they can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53675
- https://github.com/jenkinsci/warrior-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3516
- http://www.openwall.com/lists/oss-security/2025/07/09/4
