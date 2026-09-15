# [M] Jenkins Google Calendar Plugin has Insufficiently Protected Credentials

## Summary
Severity: Medium
Advisory: GHSA-8gq4-x72r-6xcr
CVE: CVE-2019-10425
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8gq4-x72r-6xcr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:gcal` — affected >=0

## Details
Google Calendar Plugin stores a calendar password unencrypted in job `config.xml` files on the Jenkins controller. This password can be viewed by users with Extended Read permission, or access to the Jenkins controller file system.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10425
- https://github.com/jenkinsci/gcal-plugin
- https://jenkins.io/security/advisory/2019-09-25/#SECURITY-1572
- http://www.openwall.com/lists/oss-security/2019/09/25/3
