# [M] Jenkins Support Core Plugin stores sensitive data in plain text

## Summary
Severity: Medium
Advisory: GHSA-5m8f-v3gw-h94w
CVE: CVE-2022-25187
CWE: CWE-212, CWE-312, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-5m8f-v3gw-h94w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:support-core` — affected >=0 <2.79.1

## Details
Jenkins Support Core Plugin 2.79 and earlier does not redact some sensitive information in the support bundle. Support Core Plugin 2.79.1 adds a list of keywords whose associated values are redacted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25187
- https://github.com/jenkinsci/support-core-plugin/commit/c6d20da4f372f03bd3e4844f0df2f109df68a63c
- https://github.com/jenkinsci/support-core-plugin/commit/e90487a87bc0a3445c887203f5badec17af905c5
- https://github.com/jenkinsci/support-core-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2186
