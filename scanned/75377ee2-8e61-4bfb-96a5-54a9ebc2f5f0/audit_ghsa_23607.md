# [M] Arbitrary file read vulnerability in workspace browsers in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-vpjm-58cw-r8q5
CVE: CVE-2021-21602
CWE: CWE-59
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vpjm-58cw-r8q5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.263.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.264 <2.275

## Details
The file browser for workspaces, archived artifacts, and `$JENKINS_HOME/userContent/` follows symbolic links to locations outside the directory being browsed in Jenkins 2.274 and earlier, LTS 2.263.1 and earlier.

This allows attackers with Job/Workspace permission and the ability to control workspace contents (e.g., with Job/Configure permission or the ability to change SCM contents) to create symbolic links that allow them to access files outside workspaces using the workspace browser.

This issue is caused by an incomplete fix for SECURITY-904 / CVE-2018-1000862 in the [2018-12-08 security advisory](https://www.jenkins.io/security/advisory/2018-12-05/#SECURITY-904).

Jenkins 2.275, LTS 2.263.2 no longer supports symlinks in workspace browsers. While they may still exist on the file system, they are no longer shown on the UI, accessible via URLs, or included in directory content downloads.

This fix only changes the behavior of the Jenkins UI. Archiving artifacts still behaves as before.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21602
- https://github.com/jenkinsci/jenkins/commit/71d2ecf1a4e5303e80815eaa3935c4f2fa3d9104
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2021-01-13/#SECURITY-1452
