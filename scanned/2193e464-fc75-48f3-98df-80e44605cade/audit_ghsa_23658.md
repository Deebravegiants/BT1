# [M] Passwords stored in plain text by Mail Commander Plugin for Jenkins-ci Plugin

## Summary
Severity: Medium
Advisory: GHSA-485q-v457-3p58
CVE: CVE-2020-2318
CWE: CWE-256, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-485q-v457-3p58
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:mailcommander` — affected >=0

## Details
Jenkins Mail Commander Plugin for Jenkins-ci Plugin 1.0.0 and earlier stores passwords unencrypted in job config.xml files on the Jenkins controller where they can be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2318
- https://github.com/jenkinsci/mail-commander-plugin
- https://www.jenkins.io/security/advisory/2020-11-04/#SECURITY-2085
