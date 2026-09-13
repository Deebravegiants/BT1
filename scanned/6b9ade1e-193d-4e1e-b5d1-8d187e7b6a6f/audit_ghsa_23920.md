# [C] Jenkins allows Execution of Code by Opening a JRMP Listener

## Summary
Severity: Critical
Advisory: GHSA-j7q5-h445-f7pc
CVE: CVE-2016-0788
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-j7q5-h445-f7pc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.643 <1.650
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.642.2

## Details
The remoting module in Jenkins before 1.650 and LTS before 1.642.2 allows remote attackers to execute arbitrary code by opening a JRMP listener.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0788
- https://github.com/jenkinsci/jenkins/commit/1ec232ca1c80e924d70212313b852aec408aa37e
- https://access.redhat.com/errata/RHSA-2016:0711
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2016-02-24
- http://rhn.redhat.com/errata/RHSA-2016-1773.html
