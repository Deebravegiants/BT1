# [M] Passwords stored in plain text by Jenkins view-cloner Plugin 

## Summary
Severity: Medium
Advisory: GHSA-6hw7-x86v-wrgf
CVE: CVE-2023-24450
CWE: CWE-256, CWE-312
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-6hw7-x86v-wrgf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:view-cloner` — affected >=0

## Details
Jenkins view-cloner Plugin 1.1 and earlier stores passwords unencrypted in job config.xml files on the Jenkins controller where they can be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24450
- https://github.com/jenkinsci/view-cloner-plugin
- https://www.jenkins.io/security/advisory/2023-01-24/#SECURITY-2787
