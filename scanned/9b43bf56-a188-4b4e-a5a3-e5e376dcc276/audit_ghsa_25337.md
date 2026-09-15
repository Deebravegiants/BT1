# [M] Memory usage graphs accessible to anyone with Overall/Read

## Summary
Severity: Medium
Advisory: GHSA-r78q-qgx6-64pp
CVE: CVE-2020-2104
CWE: CWE-285, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r78q-qgx6-64pp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.204.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.205 <2.219

## Details
Jenkins includes a feature that shows a JVM memory usage chart for the Jenkins controller.

Access to the chart in Jenkins 2.218 and earlier, LTS 2.204.1 and earlier requires no permissions beyond the general Overall/Read, allowing users who are not administrators to view JVM memory usage data.

Jenkins 2.219, LTS 2.204.2 now requires Overall/Administer permissions to view the JVM memory usage chart.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2104
- https://github.com/jenkinsci/jenkins/commit/7d44836fad0f49341ae2a61de06dbb556014a2df
- https://access.redhat.com/errata/RHBA-2020:0402
- https://access.redhat.com/errata/RHBA-2020:0675
- https://access.redhat.com/errata/RHSA-2020:0681
- https://access.redhat.com/errata/RHSA-2020:0683
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2020-01-29/#SECURITY-1650
- http://www.openwall.com/lists/oss-security/2020/01/29/1
