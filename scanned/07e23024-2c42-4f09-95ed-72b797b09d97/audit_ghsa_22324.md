# [M] Exposure of Sensitive Information to an Unauthorized Actor in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-cpw3-x7gf-p872
CVE: CVE-2018-1000169
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-cpw3-x7gf-p872
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.107.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.108 <2.116

## Details
An exposure of sensitive information vulnerability exists in Jenkins 2.115 and older, LTS 2.107.1 and older, in CLICommand.java and ViewOptionHandler.java that allows unauthorized attackers to confirm the existence of agents or views with an attacker-specified name by sending a CLI command to Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000169
- https://github.com/jenkinsci/jenkins/commit/69a784bb8d2c5a021d225eda2d392fb081c1169e
- https://access.redhat.com/errata/RHBA-2018:1816
- https://jenkins.io/security/advisory/2018-04-11/#SECURITY-754
