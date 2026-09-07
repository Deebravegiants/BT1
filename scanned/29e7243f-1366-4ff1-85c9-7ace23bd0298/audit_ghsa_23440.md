# [M] Jenkins session fixation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8jfx-h6q2-v4g3
CVE: CVE-2014-2066
CWE: CWE-287
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-8jfx-h6q2-v4g3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.533 <1.551
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.532.2

## Details
Session fixation vulnerability in Jenkins before 1.551 and LTS before 1.532.2 allows remote attackers to hijack web sessions via vectors involving the "override" of Jenkins cookies.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2066
- https://github.com/jenkinsci/jenkins/commit/8ac74c350779921598f9d5edfed39dd35de8842a
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2014-02-14
- http://www.openwall.com/lists/oss-security/2014/02/21/2
