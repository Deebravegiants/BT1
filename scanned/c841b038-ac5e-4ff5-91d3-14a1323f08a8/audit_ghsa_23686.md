# [H] Improper Restriction of XML External Entity Reference in Jenkins JUnit Plugin

## Summary
Severity: High
Advisory: GHSA-4rj6-9pjh-882r
CVE: CVE-2018-1000056
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-4rj6-9pjh-882r
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:junit` — affected >=0 <1.24

## Details
Jenkins JUnit Plugin 1.23 and earlier processes XML external entities in files it parses as part of the build process, allowing attackers with user permissions in Jenkins to extract secrets from the Jenkins master, perform server-side request forgery, or denial-of-service attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000056
- https://github.com/jenkinsci/junit-plugin/commit/15f39fc49d9f25bca872badb48e708a8bb815ea7
- https://github.com/jenkinsci/junit-plugin
- https://jenkins.io/security/advisory/2018-02-05
