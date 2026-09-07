# [H] Stored XSS vulnerability in Radiator View Plugin

## Summary
Severity: High
Advisory: GHSA-7vp5-xf5q-fxjq
CVE: CVE-2020-2263
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7vp5-xf5q-fxjq
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:radiatorviewplugin` — affected >=0

## Details
Jenkins Radiator View Plugin 1.29 and earlier does not escape the full name of the jobs in tooltips, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Job/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2263
- https://github.com/jenkinsci/radiatorview-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1927
- http://www.openwall.com/lists/oss-security/2020/09/16/3
