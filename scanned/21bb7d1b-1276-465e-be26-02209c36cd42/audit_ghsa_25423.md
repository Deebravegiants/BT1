# [M] Jenkins Vulnerable to Denial of Service (DoS) via Crafted Payload

## Summary
Severity: Medium
Advisory: GHSA-5c56-g5cq-4gj9
CVE: CVE-2013-0331
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-5c56-g5cq-4gj9
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.481 <1.502
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.480.3

## Details
Jenkins before 1.502 and LTS before 1.480.3 allows remote authenticated users with write access to cause a denial of service via a crafted payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-0331
- https://bugzilla.redhat.com/show_bug.cgi?id=914879
- https://github.com/jenkinsci/jenkins
- https://web.archive.org/web/20200229023853/http://www.securityfocus.com/bid/57994
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2013-02-16
- http://rhn.redhat.com/errata/RHSA-2013-0638.html
- http://www.cloudbees.com/jenkins-advisory/jenkins-security-advisory-2013-02-16.cb
- http://www.openwall.com/lists/oss-security/2013/02/21/7
