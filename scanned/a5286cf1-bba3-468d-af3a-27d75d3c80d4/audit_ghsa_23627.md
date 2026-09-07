# [H] Stored XSS vulnerability in Locked Files Report Plugin

## Summary
Severity: High
Advisory: GHSA-9rhc-vjjp-gccw
CVE: CVE-2020-2271
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9rhc-vjjp-gccw
Type: github-advisory

## Affected
- Maven: `org.jvnet.hudson.plugins:locked-files-report` — affected >=0

## Details
Jenkins Locked Files Report Plugin 1.6 and earlier does not escape locked files' names in tooltips, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Job/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2271
- https://github.com/jenkinsci/locked-files-report-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1921
- http://www.openwall.com/lists/oss-security/2020/09/16/3
