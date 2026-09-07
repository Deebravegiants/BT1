# [M] Stored XSS vulnerability in Jenkins Active Choices Plugin

## Summary
Severity: Medium
Advisory: GHSA-rp4x-h577-chvq
CVE: CVE-2021-21699
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rp4x-h577-chvq
Type: github-advisory

## Affected
- Maven: `org.biouno:uno-choice` — affected >=0 <2.5.7

## Details
Jenkins Active Choices Plugin 2.5.6 and earlier does not escape the parameter name of reactive parameters and dynamic reference parameters.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Job/Configure permission.

Jenkins Active Choices Plugin 2.5.7 escapes references to parameter names.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21699
- https://github.com/jenkinsci/active-choices-plugin/commit/4529ab6413d4ec70d02455536ea6c5196332ba62
- https://github.com/jenkinsci/active-choices-plugin
- https://www.jenkins.io/security/advisory/2021-11-12/#SECURITY-2219
- http://www.openwall.com/lists/oss-security/2021/11/12/1
