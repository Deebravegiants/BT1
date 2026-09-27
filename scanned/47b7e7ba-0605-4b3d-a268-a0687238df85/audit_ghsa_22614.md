# [M] Incorrect permission checks in Jenkins Config File Provider Plugin allow enumerating credentials IDs

## Summary
Severity: Medium
Advisory: GHSA-3m3f-2323-64m7
CVE: CVE-2021-21643
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3m3f-2323-64m7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:config-file-provider` — affected >=0 <3.7.1

## Details
Jenkins Config File Provider Plugin 3.7.0 and earlier does not correctly perform permission checks in several HTTP endpoints.

This allows attackers with global Job/Configure permission to enumerate system-scoped credentials IDs of credentials stored in Jenkins. Those can be used as part of an attack to capture the credentials using another vulnerability.

An enumeration of system-scoped credentials IDs in Jenkins Config File Provider Plugin 3.7.1 requires Overall/Administer permission.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21643
- https://github.com/jenkinsci/config-file-provider-plugin/commit/d615e3278358b033f5e8d0d2e3f38f467b0e29f2
- https://github.com/jenkinsci/config-file-provider-plugin
- https://www.jenkins.io/security/advisory/2021-04-21/#SECURITY-2254
- http://www.openwall.com/lists/oss-security/2021/04/21/2
