# [M] Stored Cross-site Scripting in folder-auth plugin

## Summary
Severity: Medium
Advisory: GHSA-5vjc-qx43-r747
CVE: CVE-2022-27200
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-5vjc-qx43-r747
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:folder-auth` — affected >=0 <1.4

## Details
Folder-based Authorization Strategy Plugin 1.3 and earlier does not escape the names of roles shown on the configuration form.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Overall/Administer permission.

Folder-based Authorization Strategy Plugin 1.4 escapes the names of roles shown on the configuration form.

See https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-2646

## References
- https://github.com/jenkinsci/folder-auth-plugin/security/advisories/GHSA-5vjc-qx43-r747
- https://nvd.nist.gov/vuln/detail/CVE-2022-27200
- https://github.com/jenkinsci/folder-auth-plugin/commit/085df580c22902820ebba77b1201fabff098efc4
- https://github.com/jenkinsci/folder-auth-plugin
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-2646
- http://www.openwall.com/lists/oss-security/2022/03/15/2
