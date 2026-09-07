# [M] XSS vulnerability in Jenkins useMango Runner Plugin

## Summary
Severity: Medium
Advisory: GHSA-5x89-75r7-8rjh
CVE: CVE-2020-2176
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5x89-75r7-8rjh
Type: github-advisory

## Affected
- Maven: `it.infuse.jenkins:usemango-runner` — affected >=0 <1.5

## Details
Multiple form validation endpoints in useMango Runner Plugin 1.4 and earlier do not escape values received from the useMango service.

This results in a cross-site scripting (XSS) vulnerability exploitable by users able to control the values returned from the useMango service.

useMango Runner Plugin 1.5 escapes all values received from the useMango service in form validation messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2176
- https://github.com/jenkinsci/usemango-runner-plugin
- https://jenkins.io/security/advisory/2020-04-07/#SECURITY-1780
- http://www.openwall.com/lists/oss-security/2020/04/07/3
