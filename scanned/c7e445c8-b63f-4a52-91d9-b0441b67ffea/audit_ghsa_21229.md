# [H] Cross-site Scripting in Jenkins Validating Email Parameter Plugin

## Summary
Severity: High
Advisory: GHSA-hqmp-vxj7-5wpq
CVE: CVE-2022-34791
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-01
Source: https://github.com/advisories/GHSA-hqmp-vxj7-5wpq
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:validating-email-parameter` — affected >=0

## Details
Jenkins Validating Email Parameter Plugin 1.10 and earlier does not escape the name and description of its parameter type. 

Additionally, it disables the security hardening added in Jenkins 2.44 and LTS 2.32.2 as part of the [SECURITY-353 / CVE-2017-2601](https://www.jenkins.io/security/advisory/2017-02-01/#persisted-cross-site-scripting-vulnerability-in-parameter-names-and-descriptions) fix that protects the \"Build With Parameters\" and \"Parameters\" pages from vulnerabilities like this by default.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34791
- https://github.com/jenkinsci/validating-email-parameter-plugin
- https://www.jenkins.io/security/advisory/2022-06-30/#SECURITY-2165
