# [H] Jenkins Mashup Portlets Plugin vulnerable to stored cross-site scripting

## Summary
Severity: High
Advisory: GHSA-h9h3-jx58-6hqq
CVE: CVE-2023-28679
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-02
Source: https://github.com/advisories/GHSA-h9h3-jx58-6hqq
Type: github-advisory

## Affected
- Maven: `javagh.jenkins:mashup-portlets-plugin` — affected >=0

## Details
Jenkins Mashup Portlets Plugin 1.1.2 and earlier provides the "Generic JS Portlet" feature that lets a user populate a portlet using a custom JavaScript expression.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by authenticated attackers with Overall/Read permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28679
- https://www.jenkins.io/security/advisory/2023-03-21/#SECURITY-2813
