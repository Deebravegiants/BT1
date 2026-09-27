# [M] Jenkin allows attackers to obtain passwords by reading the HTML source code

## Summary
Severity: Medium
Advisory: GHSA-rxfv-gm5x-9wqj
CVE: CVE-2014-2061
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-rxfv-gm5x-9wqj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.533 <1.551
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.532.2

## Details
The input control in PasswordParameterDefinition in Jenkins before 1.551 and LTS before 1.532.2 allows remote attackers to obtain passwords by reading the HTML source code, related to the default value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2061
- https://github.com/jenkinsci/jenkins/commit/bf539198564a1108b7b71a973bf7de963a6213ef
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2014-02-14
- http://www.openwall.com/lists/oss-security/2014/02/21/2
