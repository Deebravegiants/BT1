# [M] Cross-site Scripting in Jenkins SiteMonitor Plugin

## Summary
Severity: Medium
Advisory: GHSA-mh27-rxmr-8q4c
CVE: CVE-2022-28153
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-30
Source: https://github.com/advisories/GHSA-mh27-rxmr-8q4c
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:sitemonitor` — affected >=0

## Details
Jenkins SiteMonitor Plugin 0.6 and earlier does not escape URLs of sites to monitor in tooltips, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28153
- https://github.com/jenkinsci/sitemonitor-plugin
- https://www.jenkins.io/security/advisory/2022-03-29/#SECURITY-1932
- http://www.openwall.com/lists/oss-security/2022/03/29/1
