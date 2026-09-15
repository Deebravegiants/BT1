# [M] Infinite Loop in Jenkins Core

## Summary
Severity: Medium
Advisory: GHSA-8qpf-fv36-h4r8
CVE: CVE-2018-1999044
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8qpf-fv36-h4r8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.138

## Details
A Cron expression form validation could enter infinite loop, potentially resulting in denial of service. The form validation for cron expressions (e.g. "Poll SCM", "Build periodically") could enter infinite loops when cron expressions only matching certain rare dates were entered, blocking request handling threads indefinitely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999044
- https://github.com/jenkinsci/jenkins/commit/e5046911c57e60a1d6d8aca9b21bd9093b0f3763
- https://jenkins.io/security/advisory/2018-08-15/#SECURITY-790
