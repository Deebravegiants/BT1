# [M] Jenkins allows Remote Users to Obtain Sensitive Information from a Plugin Code

## Summary
Severity: Medium
Advisory: GHSA-5xm3-48v5-6h7v
CVE: CVE-2014-3667
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5xm3-48v5-6h7v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.566 <1.583
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.565.3

## Details
Jenkins before 1.583 and LTS before 1.565.3 does not properly prevent downloading of plugins, which allows remote authenticated users with the Overall/READ permission to obtain sensitive information by reading the plugin code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3667
- https://github.com/jenkinsci/jenkins/commit/f0a29b562e14d837912c6b35fa4e81478563813a
- https://access.redhat.com/errata/RHBA-2014:1630
- https://access.redhat.com/errata/RHSA-2016:0070
- https://access.redhat.com/security/cve/CVE-2014-3667
- https://bugzilla.redhat.com/show_bug.cgi?id=1147770
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2014-10-01
