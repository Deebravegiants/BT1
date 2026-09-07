# [H] Stored XSS vulnerability in Custom Job Icon Plugin

## Summary
Severity: High
Advisory: GHSA-wrwq-4f2h-qxj8
CVE: CVE-2020-2264
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wrwq-4f2h-qxj8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:custom-job-icon` — affected >=0

## Details
Jenkins Custom Job Icon Plugin 0.2 and earlier does not escape the job descriptions in tooltips, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Job/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2264
- https://github.com/jenkinsci/custom-job-icon-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1914
- http://www.openwall.com/lists/oss-security/2020/09/16/3
