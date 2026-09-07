# [M] Stored Cross-site Scripting vulnerability in Jenkins Favorite Plugin

## Summary
Severity: Medium
Advisory: GHSA-874r-46c6-7p4r
CVE: CVE-2022-27196
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-874r-46c6-7p4r
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:favorite` — affected >=0 <2.4.1

## Details
Jenkins Favorite Plugin 2.4.0 and earlier does not escape the names of jobs in the favorite column, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure or Item/Create permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27196
- https://github.com/jenkinsci/favorite-plugin/commit/543a4d87c4fade02173f793905a99adec517bc3b
- https://github.com/jenkinsci/favorite-plugin
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-2557
- http://www.openwall.com/lists/oss-security/2022/03/15/2
