# [M] Jenkins has a build information disclosure vulnerability through Run Parameter 

## Summary
Severity: Medium
Advisory: GHSA-wfhp-qgm8-5p5c
CVE: CVE-2026-27100
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-wfhp-qgm8-5p5c
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.542 <2.551
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.541.2

## Details
Jenkins 2.550 and earlier, LTS 2.541.1 and earlier accepts Run Parameter values that refer to builds the user submitting the build does not have access to, allowing attackers with Item/Build and Item/Configure permission to obtain information about the existence of jobs, the existence of builds, and if a specified build exists, its display name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-27100
- https://github.com/jenkinsci/jenkins/commit/f92eadb5813f04ca27439455e2573c3171e93a45
- https://github.com/jenkinsci/jenkins
- https://github.com/jenkinsci/jenkins/releases/tag/jenkins-2.541.2
- https://github.com/jenkinsci/jenkins/releases/tag/jenkins-2.551
- https://www.jenkins.io/security/advisory/2026-02-18/#SECURITY-3658
