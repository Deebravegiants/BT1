# [M] Jenkins Image Tag Parameter Plugin improperly introduces option to opt out of SSL/TLS certificate validation

## Summary
Severity: Medium
Advisory: GHSA-38jc-2rwx-qgxr
CVE: CVE-2023-30516
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-38jc-2rwx-qgxr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:image-tag-parameter` — affected >=0

## Details
Jenkins Image Tag Parameter Plugin 2.0 improperly introduces an option to opt out of SSL/TLS certificate validation when connecting to Docker registries.

Job configurations using Image Tag Parameters that were created before 2.0 will have SSL/TLS certificate validation disabled by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30516
- https://www.jenkins.io/security/advisory/2023-04-12/#SECURITY-2840
- http://www.openwall.com/lists/oss-security/2023/04/13/3
