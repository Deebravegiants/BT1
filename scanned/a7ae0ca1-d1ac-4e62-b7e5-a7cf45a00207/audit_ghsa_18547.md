# [H] Jenkins Applitools Eyes Plugin vulnerable to XSS through its Build page

## Summary
Severity: High
Advisory: GHSA-j4wf-9gx8-63f8
CVE: CVE-2025-53658
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-j4wf-9gx8-63f8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:applitools-eyes` — affected >=0 <1.16.6

## Details
Jenkins Applitools Eyes Plugin 1.16.5 and earlier does not escape the Applitools URL on the build page.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

Applitools Eyes Plugin 1.16.6 rejects Applitools URLs that contain HTML metacharacters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53658
- https://github.com/jenkinsci/applitools-eyes-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3509
- http://www.openwall.com/lists/oss-security/2025/07/09/4
