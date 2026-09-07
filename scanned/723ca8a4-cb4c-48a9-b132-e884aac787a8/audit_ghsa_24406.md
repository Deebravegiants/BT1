# [H] Stored XSS vulnerability in chosen-views-tabbar Plugin

## Summary
Severity: High
Advisory: GHSA-226h-qrg4-8236
CVE: CVE-2020-2269
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-226h-qrg4-8236
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:chosen-views-tabbar` — affected >=0

## Details
Jenkins chosen-views-tabbar Plugin 1.2 and earlier does not escape view names in the dropdown to select views, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with the ability to configure views.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2269
- https://github.com/jenkinsci/chosen-views-tabbar
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1869
- http://www.openwall.com/lists/oss-security/2020/09/16/3
