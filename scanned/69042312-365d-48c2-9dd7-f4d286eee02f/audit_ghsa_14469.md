# [M] Cross site scripting vulnerability in update-center2 

## Summary
Severity: Medium
Advisory: GHSA-pqg3-xfx2-fmqp
CVE: CVE-2023-27905
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-10
Source: https://github.com/advisories/GHSA-pqg3-xfx2-fmqp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci:update-center2` — affected >=3.13 <3.15

## Details
Jenkins update-center2 3.13 and 3.14 renders the required Jenkins core version on plugin download index pages without sanitization, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers able to provide a plugin for hosting.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27905
- https://www.jenkins.io/security/advisory/2023-03-08/#SECURITY-3063
