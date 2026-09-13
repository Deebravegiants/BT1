# [M] Jenkins has Information Disclosure via Sidepanel Widget

## Summary
Severity: Medium
Advisory: GHSA-4653-rmch-3g2g
CVE: CVE-2015-5321
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4653-rmch-3g2g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.626 <1.638
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.625.2

## Details
The sidepanel widgets in the CLI command overview and help pages in Jenkins before 1.638 and LTS before 1.625.2 allow remote attackers to obtain sensitive information via a direct request to the pages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5321
- https://github.com/jenkinsci/jenkins/commit/251bdb00ab3cf4435416f0a55fa3bccf7f58896a
- https://github.com/jenkinsci/jenkins/commit/9e439d462c28fe1c96799c89709dc5d0cb8ab8fa
- https://access.redhat.com/errata/RHSA-2016:0070
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2015-11-11
- http://rhn.redhat.com/errata/RHSA-2016-0489.html
