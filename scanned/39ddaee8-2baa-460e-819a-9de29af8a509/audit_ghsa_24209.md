# [M] Jenkins allows for Code Execution via Crafted Packet to the CLI

## Summary
Severity: Medium
Advisory: GHSA-fvfh-8mj3-23xj
CVE: CVE-2014-3666
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-fvfh-8mj3-23xj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.566 <1.583
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.565.3

## Details
Jenkins before 1.583 and LTS before 1.565.3 allows remote attackers to execute arbitrary code via a crafted packet to the CLI channel.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3666
- https://github.com/jenkinsci/jenkins/commit/be195b0e19343bff6d966029d8eea99b2c039c32
- https://access.redhat.com/errata/RHSA-2016:0070
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2014-10-01
