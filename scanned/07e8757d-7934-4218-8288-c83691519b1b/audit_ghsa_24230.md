# [M] Jenkins allows Unauthorized Viewing of Queue API Information

## Summary
Severity: Medium
Advisory: GHSA-5xmf-9vgr-53mj
CVE: CVE-2015-5324
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5xmf-9vgr-53mj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.626 <1.638
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.625.2

## Details
Jenkins before 1.638 and LTS before 1.625.2 allow remote attackers to obtain sensitive information via a direct request to queue/api.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5324
- https://github.com/jenkinsci/jenkins/commit/33b55588a6a5f844a59f2cd8940d385c6d412eb5
- https://github.com/jenkinsci/jenkins/commit/4a72e938d58598cd4bd3caa48ee9e8a3f60c30e4
- https://github.com/jenkinsci/jenkins/commit/581eb9ceb354b8a55c010d0547ff73cb6fd67a75
- https://access.redhat.com/errata/RHSA-2016:0070
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2015-11-11
- http://rhn.redhat.com/errata/RHSA-2016-0489.html
