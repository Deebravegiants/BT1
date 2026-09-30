# [M] Jenkins allows attackers to execute arbitrary jobs

## Summary
Severity: Medium
Advisory: GHSA-7fpg-pp3m-h22f
CVE: CVE-2014-2058
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7fpg-pp3m-h22f
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.533 <1.551
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.532.2

## Details
BuildTrigger in Jenkins before 1.551 and LTS before 1.532.2 allows remote authenticated users to bypass access restrictions and execute arbitrary jobs by configuring a job to trigger another job. NOTE: this vulnerability exists because of an incomplete fix for CVE-2013-7330.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2058
- https://github.com/jenkinsci/jenkins/commit/b6b2a367a7976be80a799c6a49fa6c58d778b50e
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2014-02-14
- http://www.openwall.com/lists/oss-security/2014/02/21/2
