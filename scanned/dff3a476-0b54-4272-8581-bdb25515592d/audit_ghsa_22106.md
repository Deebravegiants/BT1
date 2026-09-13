# [M] Improper permission checks allow canceling queue items and aborting builds in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-q4wp-8c99-69pw
CVE: CVE-2021-21670
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q4wp-8c99-69pw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.289.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.292 <2.300

## Details
Jenkins 2.299 and earlier, LTS 2.289.1 and earlier allows users to cancel queue items and abort builds of jobs for which they have Item/Cancel permission even when they do not have Item/Read permission.

Jenkins 2.300, LTS 2.289.2 requires that users have Item/Read permission for applicable types in addition to Item/Cancel permission.

As a workaround on earlier versions of Jenkins, do not grant Item/Cancel permission to users who do not have Item/Read permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21670
- https://github.com/jenkinsci/jenkins/commit/86b7d7e789586575522650c60d591605facb1d70
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2021-06-30/#SECURITY-2278
- http://www.openwall.com/lists/oss-security/2021/06/30/1
