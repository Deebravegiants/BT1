# [M] Jenkins Exposes Sensitive Information from Job Configuration

## Summary
Severity: Medium
Advisory: GHSA-7vvj-qqvj-h8mc
CVE: CVE-2016-3724
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-7vvj-qqvj-h8mc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.652 <2.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.651.2

## Details
Jenkins before 2.3 and LTS before 1.651.2 allow remote authenticated users with extended read access to obtain sensitive password information by reading a job configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3724
- https://access.redhat.com/errata/RHSA-2016:1206
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2016-05-11
- https://www.cloudbees.com/jenkins-security-advisory-2016-05-11
- http://rhn.redhat.com/errata/RHSA-2016-1773.html
