# [M] Jenkins iceScrum Plugin vulnerable to stored Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-2pc2-h97h-2mmw
CVE: CVE-2024-28160
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-2pc2-h97h-2mmw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:icescrum` — affected >=0

## Details
Jenkins iceScrum Plugin 1.1.6 and earlier does not sanitize iceScrum project URLs on build views, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to configure jobs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28160
- https://github.com/jenkinsci/icescrum-plugin
- https://www.jenkins.io/security/advisory/2024-03-06/#SECURITY-3248
- http://www.openwall.com/lists/oss-security/2024/03/06/3
