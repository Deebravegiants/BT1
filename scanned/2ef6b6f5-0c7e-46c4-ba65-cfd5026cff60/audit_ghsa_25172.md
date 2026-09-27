# [M] Jenkins has Local File Inclusion Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-89vc-7frq-2rfj
CVE: CVE-2015-5322
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-89vc-7frq-2rfj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.626 <1.638
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.625.2

## Details
Directory traversal vulnerability in Jenkins before 1.638 and LTS before 1.625.2 allows remote attackers to list directory contents and read arbitrary files in the Jenkins servlet resources via directory traversal sequences in a request to jnlpJars/.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5322
- https://github.com/jenkinsci/jenkins/commit/5431e397216b4ab80e58bdabcb06a0066bce6592
- https://access.redhat.com/errata/RHSA-2016:0070
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2015-11-11
- http://rhn.redhat.com/errata/RHSA-2016-0489.html
