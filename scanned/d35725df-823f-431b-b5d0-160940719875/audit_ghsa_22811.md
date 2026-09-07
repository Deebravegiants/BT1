# [M] XSS vulnerability in Jenkins notification bar

## Summary
Severity: Medium
Advisory: GHSA-98gq-6hxg-52r6
CVE: CVE-2021-21603
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-98gq-6hxg-52r6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.275
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.263.2 <2.275

## Details
Jenkins 2.274 and earlier, LTS 2.263.1 and earlier does not escape notification bar response contents (typically shown after form submissions via Apply button).

This results in a cross-site scripting (XSS) vulnerability exploitable by attackers able to influence notification bar contents.

Jenkins 2.275, LTS 2.263.2 escapes the content shown in notification bars.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21603
- https://github.com/jenkinsci/jenkins/commit/f5d98421604e44f398e7de9d222b191a705608af
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2021-01-13/#SECURITY-1889
