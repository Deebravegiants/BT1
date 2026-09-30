# [H] XXE vulnerability Jenkins Warnings Plugin

## Summary
Severity: High
Advisory: GHSA-p498-rpcw-3578
CVE: CVE-2018-1000012
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-p498-rpcw-3578
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:warnings` — affected >=0 <4.65

## Details
Jenkins Warnings Plugin 4.64 and earlier processes XML external entities in files it parses as part of the build process, allowing attackers with user permissions in Jenkins to extract secrets from the Jenkins master, perform server-side request forgery, or denial-of-service attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000012
- https://jenkins.io/security/advisory/2018-01-22
