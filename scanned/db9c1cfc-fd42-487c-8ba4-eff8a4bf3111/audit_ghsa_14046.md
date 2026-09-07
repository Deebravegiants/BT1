# [H] TestComplete support Plugin vulnerable to stored Cross-site Scripting

## Summary
Severity: High
Advisory: GHSA-5wpg-qcmj-48wh
CVE: CVE-2023-33002
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-5wpg-qcmj-48wh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:TestComplete` — affected >=0

## Details
TestComplete support Plugin 2.8.1 and earlier does not escape the TestComplete project name in its test result page.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-33002
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-2892
