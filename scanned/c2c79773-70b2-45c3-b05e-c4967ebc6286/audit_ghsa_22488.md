# [M] Jenkins allows Remote Users to Inject Build Parameters

## Summary
Severity: Medium
Advisory: GHSA-qf2h-h3xq-j93j
CVE: CVE-2016-3721
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qf2h-h3xq-j93j
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.660 <2.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.651.2

## Details
Jenkins before 2.3 and LTS before 1.651.2 might allow remote authenticated users to inject arbitrary build parameters into the build environment via environment variables.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3721
- https://access.redhat.com/errata/RHSA-2016:1206
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/JENKINS/Plugins+affected+by+fix+for+SECURITY-170
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2016-05-11
- https://www.cloudbees.com/jenkins-security-advisory-2016-05-11
- http://rhn.redhat.com/errata/RHSA-2016-1773.html
- http://www.openwall.com/lists/oss-security/2024/05/02/3
