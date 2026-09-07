# [H] Jenkins Sonargraph Integration Plugin vulnerable to Stored Cross-site Scripting

## Summary
Severity: High
Advisory: GHSA-wmxx-2pvr-x7j6
CVE: CVE-2023-35145
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-14
Source: https://github.com/advisories/GHSA-wmxx-2pvr-x7j6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:sonargraph-integration` — affected >=0

## Details
Jenkins Sonargraph Integration Plugin 5.0.1 and earlier does not correctly escape the file path and the project name for the Log file field form validation.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-35145
- https://www.jenkins.io/security/advisory/2023-06-14/#SECURITY-3155
- http://www.openwall.com/lists/oss-security/2023/06/14/5
