# [M] Stored Cross-site Scripting vulnerability in Jenkins Team Views Plugin

## Summary
Severity: Medium
Advisory: GHSA-mv5c-724f-3fq7
CVE: CVE-2022-25203
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-mv5c-724f-3fq7
Type: github-advisory

## Affected
- Maven: `com.sonymobile.jenkins.plugins.teamviews:team-views` — affected >=0

## Details
Jenkins Team Views Plugin 0.9.0 and earlier does not escape team names, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Overall/Read permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25203
- https://github.com/jenkinsci/team-views-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2324
