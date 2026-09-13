# [H] XXE vulnerability in Jenkins PMD Plugin

## Summary
Severity: High
Advisory: GHSA-687x-269m-7cv9
CVE: CVE-2018-1000008
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-687x-269m-7cv9
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:pmd` — affected >=0 <3.50

## Details
Jenkins PMD Plugin 3.49 and earlier processes XML external entities in files it parses as part of the build process, allowing attackers with user permissions in Jenkins to extract secrets from the Jenkins master, perform server-side request forgery, or denial-of-service attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000008
- https://jenkins.io/security/advisory/2018-01-22
- http://www.securityfocus.com/bid/102844
