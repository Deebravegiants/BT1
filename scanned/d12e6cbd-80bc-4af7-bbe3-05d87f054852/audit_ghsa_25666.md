# [M] Jenkins allows Cross-Site Scripting (XSS) via Crafted URL

## Summary
Severity: Medium
Advisory: GHSA-x97g-3gp9-cf2p
CVE: CVE-2012-4439
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-23
Source: https://github.com/advisories/GHSA-x97g-3gp9-cf2p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.466.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.467 <1.482

## Details
Cross-site Scripting (XSS) in Jenkins main before 1.482 and LTS before 1.466.2 allows remote attackers to inject arbitrary web script or HTML via a crafted URL that points to Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-4439
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2012-4439
- https://github.com/jenkinsci/jenkins
- https://security-tracker.debian.org/tracker/CVE-2012-4439
- https://www.cloudbees.com/jenkins-security-advisory-2012-09-17
- http://www.openwall.com/lists/oss-security/2012/09/21/2
