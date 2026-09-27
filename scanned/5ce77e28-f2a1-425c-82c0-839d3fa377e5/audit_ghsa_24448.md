# [M] Jenkins allows Administrators to Access API Tokens

## Summary
Severity: Medium
Advisory: GHSA-x4m5-j4x4-4wjg
CVE: CVE-2015-5323
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-x4m5-j4x4-4wjg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.625.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.626 <1.638

## Details
Jenkins before 1.638 and LTS before 1.625.2 do not properly restrict access to API tokens which might allow remote administrators to gain privileges and run scripts by using an API token of another user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5323
- https://github.com/jenkinsci/jenkins/commit/b3f16489ad5f15c3e749ed066cf6b4251f6668c6
- https://access.redhat.com/errata/RHSA-2016:0070
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2015-11-11
- http://rhn.redhat.com/errata/RHSA-2016-0489.html
