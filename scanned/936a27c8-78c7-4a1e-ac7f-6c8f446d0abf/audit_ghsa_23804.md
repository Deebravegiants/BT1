# [M] Missing Authorization in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-p8x8-p473-mmmv
CVE: CVE-2017-1000400
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-p8x8-p473-mmmv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.73.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.74 <2.84

## Details
The Jenkins 2.73.1 and earlier, 2.83 and earlier remote API at /job/(job-name)/api contained information about upstream and downstream projects. This included information about tasks that the current user otherwise has no access to, e.g. due to lack of Item/Read permission. This has been fixed, and the API now only lists upstream and downstream projects that the current user has access to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000400
- https://github.com/jenkinsci/jenkins/commit/b2083a387a5bdb6f7ee7f7c81a1f6312aca2a558
- https://github.com/jenkinsci/jenkins
- https://github.com/jenkinsci/jenkins/blob/6d179998e18adfbaa4e443c7e837135bf36c53d7/test/src/test/java/hudson/model/AbstractProjectTest.java
- https://jenkins.io/security/advisory/2017-10-11
