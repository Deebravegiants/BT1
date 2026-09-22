# [M] Improper Authentication in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-m93h-5qmx-pphg
CVE: CVE-2017-2604
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-m93h-5qmx-pphg
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.32.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.34 <2.44

## Details
In Jenkins before versions 2.44 and 2.32.2, low privilege users were able to act on administrative monitors due to them not being consistently protected by permission checks (SECURITY-371).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2604
- https://github.com/jenkinsci/jenkins/commit/6efcf6c2ac39bc5c59ac7251822be8ddf67ceaf8
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2604
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2017-02-01
