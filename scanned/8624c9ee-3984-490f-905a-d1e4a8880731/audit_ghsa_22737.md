# [M] Jenkins Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r5m2-g5gc-q43r
CVE: CVE-2014-3661
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-r5m2-g5gc-q43r
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.566 <1.583
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.565.3

## Details
Jenkins before 1.583 and LTS before 1.565.3 allows remote attackers to cause a denial of service (thread consumption) via vectors related to a CLI handshake.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3661
- https://access.redhat.com/errata/RHBA-2014:1630
- https://access.redhat.com/errata/RHSA-2016:0070
- https://access.redhat.com/security/cve/CVE-2014-3661
- https://bugzilla.redhat.com/show_bug.cgi?id=1147758
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2014-10-01
