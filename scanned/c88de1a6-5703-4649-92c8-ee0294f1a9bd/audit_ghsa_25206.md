# [M] Jenkins allows Bypass of Access Restrictions

## Summary
Severity: Medium
Advisory: GHSA-x2q2-8pwq-fr5r
CVE: CVE-2015-5325
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-x2q2-8pwq-fr5r
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.625.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.626 <1.638

## Details
Jenkins before 1.638 and LTS before 1.625.2 allow attackers to bypass intended slave-to-master access restrictions by leveraging a JNLP slave. NOTE: this vulnerability exists because of an incomplete fix for CVE-2014-3665.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5325
- https://github.com/jenkinsci/jenkins/commit/054a329c59171ca12ff98f7063ce7fd053ee08bf
- https://access.redhat.com/errata/RHSA-2016:0070
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2015-11-11
- http://rhn.redhat.com/errata/RHSA-2016-0489.html
