# [H] XXE vulnerability in Jenkins Checkstyle Plugin

## Summary
Severity: High
Advisory: GHSA-jfj9-7j5w-6xgx
CVE: CVE-2018-1000009
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-jfj9-7j5w-6xgx
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:checkstyle` — affected >=0 <3.50

## Details
Jenkins Checkstyle Plugin 3.49 and earlier processes XML external entities in files it parses as part of the build process, allowing attackers with user permissions in Jenkins to extract secrets from the Jenkins master, perform server-side request forgery, or denial-of-service attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000009
- https://jenkins.io/security/advisory/2018-01-22
