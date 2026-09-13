# [M] Plaintext Storage of a Password in Jenkins Configuration as Code Plugin

## Summary
Severity: Medium
Advisory: GHSA-ggmx-pq89-7mcr
CVE: CVE-2019-10345
CWE: CWE-256, CWE-522, CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-ggmx-pq89-7mcr
Type: github-advisory

## Affected
- Maven: `io.jenkins:configuration-as-code` — affected >=0 <1.25

## Details
Jenkins Configuration as Code Plugin prior to version 1.25 did not treat the proxy password as a secret to be masked when logging or encrypted for export.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10345
- https://github.com/jenkinsci/configuration-as-code-plugin/commit/73afe3cb10a723cb06e29c2e5499206aadae3a0d
- https://github.com/jenkinsci/configuration-as-code-plugin
- https://jenkins.io/security/advisory/2019-07-31/#SECURITY-1303
- http://www.openwall.com/lists/oss-security/2019/07/31/1
