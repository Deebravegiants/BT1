# [M] Jenkins Credentials Binding Plugin vulnerability can expose sensitive information in logger messages

## Summary
Severity: Medium
Advisory: GHSA-9768-hprv-crj5
CVE: CVE-2025-53650
CWE: CWE-522, CWE-779
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-9768-hprv-crj5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:credentials-binding` — affected >=0 <687.689.v1a

## Details
Jenkins Credentials Binding Plugin 687.v619cb_15e923f and earlier does not properly mask (i.e., replace with asterisks) credentials present in exception error messages that are written to the build log.

Credentials Binding Plugin 687.689.v1a_f775332fc9 rethrows exceptions that contain credentials, masking those credentials in the error messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53650
- https://github.com/jenkinsci/credentials-binding-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3499
- http://www.openwall.com/lists/oss-security/2025/07/09/4
