# [H] Improper Input Validation in Jenkins Script Security Plugin

## Summary
Severity: High
Advisory: GHSA-qvmf-36h5-3f5v
CVE: CVE-2020-2110
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-qvmf-36h5-3f5v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1.70

## Details
Sandbox protection in Jenkins Script Security Plugin 1.69 and earlier could be circumvented during the script compilation phase by applying AST transforming annotations to imports or by using them inside of other annotations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2110
- https://github.com/jenkinsci/script-security-plugin/commit/1a09bdcf789b87c4e158aacebd40937c64398de3
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1713
- http://www.openwall.com/lists/oss-security/2020/02/12/3
