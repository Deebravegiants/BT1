# [H] Path Traversal in Jenkins

## Summary
Severity: High
Advisory: GHSA-x646-m7x2-gcp7
CVE: CVE-2018-1000194
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-x646-m7x2-gcp7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.107.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.108 <2.121

## Details
A path traversal vulnerability exists in Jenkins 2.120 and older, LTS 2.107.2 and older in FilePath.java, SoloFilePathFilter.java that allows malicious agents to read and write arbitrary files on the Jenkins master, bypassing the agent-to-master security subsystem protection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000194
- https://github.com/jenkinsci/jenkins/commit/5cf0a77d44310523b763698f67d645c1f2427f30
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2018-05-09/#SECURITY-788
- https://www.oracle.com/security-alerts/cpuapr2022.html
