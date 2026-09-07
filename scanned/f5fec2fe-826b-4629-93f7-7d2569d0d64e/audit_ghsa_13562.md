# [H] Jenkins Edgewall Trac Plugin vulnerable to Stored XSS

## Summary
Severity: High
Advisory: GHSA-jwx3-2hq3-682c
CVE: CVE-2023-46659
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-jwx3-2hq3-682c
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:trac` — affected >=0

## Details
Jenkins Edgewall Trac Plugin 1.13 and earlier does not escape the Trac website URL on the build page.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46659
- https://github.com/jenkinsci/trac-plugin
- https://www.jenkins.io/security/advisory/2023-10-25/#SECURITY-3247
- http://www.openwall.com/lists/oss-security/2023/10/25/2
