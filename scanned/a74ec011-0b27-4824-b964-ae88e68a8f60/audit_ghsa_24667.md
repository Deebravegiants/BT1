# [M] Improper Encoding or Escaping of Output in Jenkins Configuration as Code Plugin

## Summary
Severity: Medium
Advisory: GHSA-5r6p-p9r6-r326
CVE: CVE-2019-10362
CWE: CWE-116
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5r6p-p9r6-r326
Type: github-advisory

## Affected
- Maven: `io.jenkins:configuration-as-code` — affected >=0 <1.25

## Details
Jenkins Configuration as Code Plugin 1.24 and earlier did not escape values resulting in variable interpolation during configuration import when exporting, allowing attackers with permission to change Jenkins system configuration to obtain the values of environment variables.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10362
- https://github.com/jenkinsci/configuration-as-code-plugin/commit/b48a292112c532ab1447b864c7d30c2cae733ac8
- https://jenkins.io/security/advisory/2019-07-31/#SECURITY-1446
- http://www.openwall.com/lists/oss-security/2019/07/31/1
