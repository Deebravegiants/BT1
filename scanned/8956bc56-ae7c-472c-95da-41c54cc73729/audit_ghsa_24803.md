# [H] Jenkins Aqua Security Scanner Plugin showed plain text password in configuration form 

## Summary
Severity: High
Advisory: GHSA-xp44-8vwr-xwmv
CVE: CVE-2019-10428
CWE: CWE-319
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xp44-8vwr-xwmv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:aqua-security-scanner` — affected >=0 <3.0.18

## Details
Jenkins Aqua Security Scanner Plugin 3.0.17 and earlier transmitted configured credentials in plain text as part of the global Jenkins configuration form, potentially resulting in their exposure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10428
- https://jenkins.io/security/advisory/2019-09-25/#SECURITY-1508
- http://www.openwall.com/lists/oss-security/2019/09/25/3
