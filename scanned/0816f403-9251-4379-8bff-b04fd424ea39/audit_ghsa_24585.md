# [H] Stored XSS vulnerability in Jenkins Cadence vManager Plugin

## Summary
Severity: High
Advisory: GHSA-v46q-xjp5-7p6r
CVE: CVE-2020-2243
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-v46q-xjp5-7p6r
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:vmanager-plugin` — affected >=0 <3.0.5

## Details
Jenkins Cadence vManager Plugin 3.0.4 and earlier does not escape build descriptions in tooltips, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Run/Update permission.

Cadence vManager Plugin 3.0.5 removes affected tooltips.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2243
- https://github.com/jenkinsci/vmanager-plugin
- https://jenkins.io/security/advisory/2020-09-01/#SECURITY-1936
- http://www.openwall.com/lists/oss-security/2020/09/01/3
