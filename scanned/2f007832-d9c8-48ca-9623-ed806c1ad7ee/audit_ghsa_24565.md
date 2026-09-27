# [H] XXE vulnerability in Jenkins DRY Plugin

## Summary
Severity: High
Advisory: GHSA-x7qf-qh3r-mx22
CVE: CVE-2018-1000010
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-x7qf-qh3r-mx22
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:dry` — affected >=0 <2.50

## Details
Jenkins DRY Plugin 2.49 and earlier processes XML external entities in files it parses as part of the build process, allowing attackers with user permissions in Jenkins to extract secrets from the Jenkins master, perform server-side request forgery, or denial-of-service attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000010
- https://jenkins.io/security/advisory/2018-01-22
