# [M] Improper permission checks in Jenkins Swarm Plugin

## Summary
Severity: Medium
Advisory: GHSA-j852-mp82-wv2g
CVE: CVE-2020-2191
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j852-mp82-wv2g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:swarm` — affected >=0 <3.21

## Details
Swarm Plugin adds API endpoints to add or remove agent labels. In Swarm Plugin 3.20 and earlier these only require a global Swarm secret to use, and no regular permission check is performed. This allows users with Agent/Create permission to add or remove labels of any agent.

Swarm Plugin 3.21 requires Agent/Configure permission for the affected agent to these endpoints. It no longer uses the global Swarm secret for these API endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2191
- https://github.com/jenkinsci/swarm-plugin/commit/4d18f98b00e4c84b152d52346fb9ef1a227b1cf7
- https://github.com/jenkinsci/swarm-plugin
- https://jenkins.io/security/advisory/2020-06-03/#SECURITY-1200
- http://www.openwall.com/lists/oss-security/2020/06/03/3
