# [M] Missing permission check in Jenkins Favorite Plugin

## Summary
Severity: Medium
Advisory: GHSA-268v-2qq7-84pf
CVE: CVE-2017-1000243
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-268v-2qq7-84pf
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:favorite` — affected >=0 <2.3.0

## Details
Jenkins Favorite Plugin up to and including 2.1.0 does not perform permission checks when changing favorite status, allowing any user to set any other user's favorites

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000243
- https://github.com/jenkinsci/favorite-plugin
- https://jenkins.io/security/advisory/2017-06-06
- http://www.securityfocus.com/bid/101946
