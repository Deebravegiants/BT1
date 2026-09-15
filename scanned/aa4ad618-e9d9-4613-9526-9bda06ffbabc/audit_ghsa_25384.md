# [M] Jenkins allows attackers to configure restricted projects

## Summary
Severity: Medium
Advisory: GHSA-h5jv-hg68-mjhg
CVE: CVE-2013-7330
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-h5jv-hg68-mjhg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.481 <1.502
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.480.3

## Details
Jenkins before 1.502 allows remote authenticated users to configure an otherwise restricted project via vectors related to post-build actions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7330
- https://github.com/jenkinsci/jenkins/commit/36342d71e29e0620f803a7470ce96c61761648d8
- https://github.com/jenkinsci/jenkins/commit/757bc8a53956e6fbab267214e6e0896f03c3c262
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2014-02-14
- http://www.openwall.com/lists/oss-security/2014/02/21/2
