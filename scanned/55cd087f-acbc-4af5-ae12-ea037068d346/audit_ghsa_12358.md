# [H] Arbitrary file deletion vulnerability in Jenkins Scriptler Plugin 

## Summary
Severity: High
Advisory: GHSA-xcrr-x93h-rv4v
CVE: CVE-2023-50764
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-xcrr-x93h-rv4v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:scriptler` — affected >=0

## Details
Jenkins Scriptler Plugin 342.v6a_89fd40f466 and earlier does not restrict a file name query parameter in an HTTP endpoint, allowing attackers with Scriptler/Configure permission to delete arbitrary files on the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50764
- https://www.jenkins.io/security/advisory/2023-12-13/#SECURITY-3205
- http://www.openwall.com/lists/oss-security/2023/12/13/4
