# [H] Arbitrary code execution vulnerability in Jenkins Speaks! Plugin

## Summary
Severity: High
Advisory: GHSA-5532-prrf-rf5x
CVE: CVE-2017-1000403
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5532-prrf-rf5x
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:speaks` — affected >=0

## Details
Jenkins Speaks! Plugin, all current versions, allows users with Job/Configure permission to run arbitrary Groovy code inside the Jenkins JVM, effectively elevating privileges to Overall/Run Scripts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000403
- https://jenkins.io/security/advisory/2017-10-11
