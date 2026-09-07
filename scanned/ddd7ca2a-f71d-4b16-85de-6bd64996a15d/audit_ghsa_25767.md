# [M] CSRF vulnerability and missing permission checks in Extended Choice Parameter Plugin allow SSRF

## Summary
Severity: Medium
Advisory: GHSA-x95c-qrqr-2v27
CVE: CVE-2022-27205
CWE: CWE-276, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-x95c-qrqr-2v27
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:extended-choice-parameter` — affected >=0

## Details
Extended Choice Parameter Plugin 346.vd87693c5a_86c and earlier does not perform a permission check on form validation methods. This allows attackers with Overall/Read permission to connect to an attacker-specified URL.

Additionally, these form validation methods do not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27205
- https://github.com/jenkinsci/extended-choice-parameter-plugin
- https://www.jenkins.io/security/advisory/2022-03-15/#SECURITY-1350
- http://www.openwall.com/lists/oss-security/2022/03/15/2
