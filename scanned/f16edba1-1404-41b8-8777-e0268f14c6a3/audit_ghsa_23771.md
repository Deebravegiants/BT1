# [M] Stored XSS vulnerability in Jenkins VncRecorder Plugin

## Summary
Severity: Medium
Advisory: GHSA-vqp8-h53h-3jfh
CVE: CVE-2020-2205
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vqp8-h53h-3jfh
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:vncrecorder` — affected >=0 <1.35

## Details
VncRecorder Plugin 1.25 and earlier does not escape a tool path in the `checkVncServ` form validation endpoint accessed e.g. via job configuration forms.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by Jenkins administrators.

VncRecorder Plugin 1.35 escapes the tool path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2205
- https://github.com/jenkinsci/vncrecorder-plugin
- https://jenkins.io/security/advisory/2020-07-02/#SECURITY-1728%20(1)
- http://www.openwall.com/lists/oss-security/2020/07/02/7
