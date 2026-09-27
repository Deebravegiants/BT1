# [M] Time-of-check Time-of-use (TOCTOU) Race Condition in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-qxp6-27gw-99cj
CVE: CVE-2021-21615
CWE: CWE-367
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qxp6-27gw-99cj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.263.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.264 <2.276

## Details
Due to a time-of-check to time-of-use (TOCTOU) race condition, the file browser for workspaces, archived artifacts, and `$JENKINS_HOME/userContent/` follows symbolic links to locations outside the directory being browsed in Jenkins 2.275 and LTS 2.263.2.

This allows attackers with Job/Workspace permission and the ability to control workspace contents, e.g., with Job/Configure permission or the ability to change SCM contents, to create symbolic links that allow them to access files outside workspaces using the workspace browser.

This issue is caused by an incorrectly applied fix for SECURITY-1452 / CVE-2021-21602 in the [2021-01-13 security advisory](https://www.jenkins.io/security/advisory/2021-01-13/#SECURITY-1452).

Jenkins 2.276, LTS 2.263.3 no longer differentiates the check and the use of symlinks in workspace browsers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21615
- https://www.jenkins.io/security/advisory/2021-01-26/#SECURITY-2197
- http://www.openwall.com/lists/oss-security/2021/01/26/2
