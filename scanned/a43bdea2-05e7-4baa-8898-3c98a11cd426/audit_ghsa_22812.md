# [M] Incorrect Permission Assignment for Critical Resource in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-wf9g-rh76-6jvr
CVE: CVE-2017-2612
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wf9g-rh76-6jvr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.32.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.34 <2.44

## Details
In Jenkins before versions 2.44, 2.32.2 low privilege users were able to override JDK download credentials (SECURITY-392), resulting in future builds possibly failing to download a JDK.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2612
- https://github.com/jenkinsci/jenkins/commit/a814154695e23dc37542af7d40cacc129cf70722
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2612
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2017-02-01
