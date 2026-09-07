# [M] Reflected XSS vulnerability in Jenkins VncViewer Plugin

## Summary
Severity: Medium
Advisory: GHSA-2j4h-cjgh-659v
CVE: CVE-2020-2207
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2j4h-cjgh-659v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:vncviewer` — affected >=0 <1.8

## Details
VncViewer Plugin 1.7 and earlier does not escape a parameter value in the `checkVncServ` form validation endpoint output.

This results in a reflected cross-site scripting (XSS) vulnerability.

VncViewer Plugin 1.8 escapes the parameter value in the output.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2207
- https://github.com/jenkinsci/vncviewer-plugin/commit/99b2aa3ed0857ef35de9a3aca0b0c53add3b392d
- https://github.com/jenkinsci/vncviewer-plugin
- https://jenkins.io/security/advisory/2020-07-02/#SECURITY-1776
- http://www.openwall.com/lists/oss-security/2020/07/02/7
