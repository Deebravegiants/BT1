# [M] Inadequate Encryption Strength in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-r9q2-3r6x-qmgp
CVE: CVE-2017-2598
CWE: CWE-326
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-r9q2-3r6x-qmgp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.32.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.34 <2.44

## Details
Jenkins before versions 2.44 and 2.32.2 uses AES ECB block cipher mode without IV for encrypting secrets which makes Jenkins and the stored secrets vulnerable to unnecessary risks (SECURITY-304).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2598
- https://github.com/jenkinsci/jenkins/commit/e6aa166246d1734f4798a9e31f78842f4c85c28b
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2598
- https://github.com/jenkinsci/jenkins
- https://jenkins.io/security/advisory/2017-02-01
