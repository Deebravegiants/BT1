# [M] Path traversal vulnerability in Jenkins Subversion Plugin allows reading arbitrary files

## Summary
Severity: Medium
Advisory: GHSA-q58j-fhj7-j6fg
CVE: CVE-2021-21698
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q58j-fhj7-j6fg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:subversion` — affected >=0 <2.15.1

## Details
Subversion Plugin 2.15.0 and earlier does not restrict the name of a file when looking up a subversion key file on the controller from an agent.

This allows attackers able to control agent processes to read arbitrary files on the Jenkins controller file system.

Subversion Plugin 2.15.1 checks for the presence of and prohibits directory separator characters as part of the file name, restricting it to the intended directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21698
- https://github.com/jenkinsci/subversion-plugin/commit/7d1525edea6641a2febd3f7deeac55c0a89b0d7e
- https://github.com/jenkinsci/subversion-plugin
- https://www.jenkins.io/security/advisory/2021-11-04/#SECURITY-2506
- http://www.openwall.com/lists/oss-security/2021/11/04/3
