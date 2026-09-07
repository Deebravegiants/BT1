# [M] Jenkins Exposure of Sensitive Information to an Unauthorized Actor vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fxqr-px2m-fvc2
CVE: CVE-2014-3662
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-fxqr-px2m-fvc2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.566 <1.583
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.565.3

## Details
Jenkins before 1.583 and LTS before 1.565.3 allows remote attackers to enumerate user names via vectors related to login attempts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3662
- https://access.redhat.com/errata/RHBA-2014:1630
- https://access.redhat.com/errata/RHSA-2016:0070
- https://access.redhat.com/security/cve/CVE-2014-3662
- https://bugzilla.redhat.com/show_bug.cgi?id=1147759
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2014-10-01
