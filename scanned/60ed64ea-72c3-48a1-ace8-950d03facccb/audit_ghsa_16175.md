# [H] Stored XSS vulnerability in Jenkins Authorize Project Plugin 

## Summary
Severity: High
Advisory: GHSA-8886-8v27-85j8
CVE: CVE-2024-52552
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-13
Source: https://github.com/advisories/GHSA-8886-8v27-85j8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:authorize-project` — affected >=0 <1.8.0

## Details
Jenkins Authorize Project Plugin 1.7.2 and earlier evaluates a string containing the job name with JavaScript on the Authorization view, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission. This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission. Authorize Project Plugin 1.8.0 no longer evaluates a string containing the job name with JavaScript on the Authorization view.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-52552
- https://github.com/jenkinsci/authorize-project-plugin
- https://www.jenkins.io/security/advisory/2024-11-13/#SECURITY-3010
