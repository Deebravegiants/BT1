# [M] User passwords transmitted in plain text by Jenkins Active Directory Plugin

## Summary
Severity: Medium
Advisory: GHSA-c8cc-hj57-vm65
CVE: CVE-2022-23105
CWE: CWE-319
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-13
Source: https://github.com/advisories/GHSA-c8cc-hj57-vm65
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:active-directory` — affected >=0 <2.25.1

## Details
Jenkins Active Directory Plugin 2.25 and earlier does not encrypt the transmission of data between the Jenkins controller and Active Directory servers in most configurations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23105
- https://github.com/jenkinsci/active-directory-plugin/commit/07b05f83b167c79590f2efbdad8cb84fc98ed150
- https://github.com/jenkinsci/active-directory-plugin
- https://www.jenkins.io/security/advisory/2022-01-12/#SECURITY-1389
- http://www.openwall.com/lists/oss-security/2022/01/12/6
