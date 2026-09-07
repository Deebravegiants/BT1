# [H] Stored XSS vulnerability in Description Column Plugin

## Summary
Severity: High
Advisory: GHSA-qxrx-m6v6-m767
CVE: CVE-2020-2266
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qxrx-m6v6-m767
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:description-column-plugin` — affected >=0

## Details
Jenkins Description Column Plugin 1.3 and earlier does not escape the job description in the column tooltip, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Job/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2266
- https://github.com/jenkinsci/description-column-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1916
- http://www.openwall.com/lists/oss-security/2020/09/16/3
