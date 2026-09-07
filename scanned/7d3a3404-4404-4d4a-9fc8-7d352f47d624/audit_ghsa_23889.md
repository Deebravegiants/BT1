# [M] Jenkins allows for Privilege Escalation by Remote Authenticated Users

## Summary
Severity: Medium
Advisory: GHSA-3269-jqp5-v8c9
CVE: CVE-2015-1814
CWE: CWE-266
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-3269-jqp5-v8c9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.597 <1.606
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.596.2

## Details
The API token-issuing service in Jenkins before 1.606 and LTS before 1.596.2 allows remote attackers to gain privileges via a "forced API token change" involving anonymous users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1814
- https://github.com/jenkinsci/jenkins/commit/57e78880cc035874bda916ef4d8d7fd7642af9db
- https://access.redhat.com/errata/RHSA-2016:0070
- https://bugzilla.redhat.com/show_bug.cgi?id=1205616
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2015-03-23
- http://rhn.redhat.com/errata/RHSA-2015-1844.html
