# [M] Non-constant time comparison of inbound TCP agent connection secret

## Summary
Severity: Medium
Advisory: GHSA-w7jr-wqw6-54xc
CVE: CVE-2020-2101
CWE: CWE-203, CWE-208
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w7jr-wqw6-54xc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.204.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.205 <2.219

## Details
Jenkins 2.218 and earlier, LTS 2.204.1 and earlier does not use a constant-time comparison validating the connection secret when an inbound TCP agent connection is initiated. This could potentially allow attackers to use statistical methods to obtain the connection secret.

Jenkins 2.219, LTS 2.204.2 now uses a constant-time comparison function for verifying connection secrets.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2101
- https://github.com/jenkinsci/jenkins/commit/0ba36508187ff771bba87feaf03057496775064c
- https://access.redhat.com/errata/RHBA-2020:0402
- https://access.redhat.com/errata/RHBA-2020:0675
- https://access.redhat.com/errata/RHSA-2020:0681
- https://access.redhat.com/errata/RHSA-2020:0683
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2020-01-29/#SECURITY-1659
- http://www.openwall.com/lists/oss-security/2020/01/29/1
