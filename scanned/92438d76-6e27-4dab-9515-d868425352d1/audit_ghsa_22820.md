# [M] Reflected XSS vulnerability in Jenkins VncRecorder Plugin

## Summary
Severity: Medium
Advisory: GHSA-fq52-6cjf-jw59
CVE: CVE-2020-2206
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fq52-6cjf-jw59
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:vncrecorder` — affected >=0 <1.35

## Details
VncRecorder Plugin 1.25 and earlier does not escape a parameter value in the `checkVncServ` form validation endpoint output.

This results in a reflected cross-site scripting (XSS) vulnerability.

VncRecorder Plugin 1.35 escapes the parameter value in the output.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2206
- https://github.com/jenkinsci/vncrecorder-plugin
- https://jenkins.io/security/advisory/2020-07-02/#SECURITY-1728%20(2)
- http://www.openwall.com/lists/oss-security/2020/07/02/7
