# [M] Path traversal vulnerability on Windows in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-4pw5-r58h-fv24
CVE: CVE-2021-21683
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4pw5-r58h-fv24
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.303.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.304 <2.315

## Details
The file browser for workspaces, archived artifacts, and `userContent/` in Jenkins 2.314 and earlier, LTS 2.303.1 and earlier may interpret some paths to files as absolute on Windows.

This results in a path traversal vulnerability allowing attackers with Overall/Read permission (Windows controller) or Job/Workspace permission (Windows agents) to obtain the contents of arbitrary files.\n\nThe file browser in Jenkins 2.315, LTS 2.303.2 refuses to serve files that would be considered absolute paths.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21683
- https://github.com/jenkinsci/jenkins/commit/3f679fc12d073676a4441d3fa8b5fff34c07662f
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2021-10-06/#SECURITY-2481
- http://www.openwall.com/lists/oss-security/2021/10/06/1
