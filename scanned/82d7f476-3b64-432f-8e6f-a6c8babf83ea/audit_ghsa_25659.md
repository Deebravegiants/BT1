# [M] Jenkins Violation Plugin allows Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-5qpv-27q3-6484
CVE: CVE-2012-4440
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-23
Source: https://github.com/advisories/GHSA-5qpv-27q3-6484
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:violations` — affected >=0 <0.7.11

## Details
Cross-site Scripting (XSS) in Jenkins main before 1.482 and LTS before 1.466.2 allows remote attackers to inject arbitrary web script or HTML in the Violations plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-4440
- https://github.com/jenkinsci/violations-plugin/commit/6dcbef2114adb0f9c01a0a927105fcf80a414e4d
- https://github.com/jenkinsci/violations-plugin
- https://security-tracker.debian.org/tracker/CVE-2012-4440
- https://www.cloudbees.com/jenkins-security-advisory-2012-09-17
- http://www.openwall.com/lists/oss-security/2012/09/21/2
