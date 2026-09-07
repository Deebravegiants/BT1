# [M] Jenkins Token Macro Plugin's recursive token expansion results in information disclosure and DoS

## Summary
Severity: Medium
Advisory: GHSA-23h9-m55m-c5jp
CVE: CVE-2019-1003011
CWE: CWE-674
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-23h9-m55m-c5jp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:token-macro` — affected >=0 <2.6

## Details
Jenkins Token Macro Plugin recursively applied token expansion.

This could be used by users able to affect input to token expansion (such as change log messages), to inject additional tokens into the input, which would then be expanded, resulting in information disclosure (for example values of environment variables), or denial of service.

Most tokens have been changed to no longer recursively apply token expansion.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003011
- https://github.com/jenkinsci/token-macro-plugin/commit/70163600031ea8d43833e6eea928f8fa2e44f96a
- https://access.redhat.com/errata/RHBA-2019:0326
- https://access.redhat.com/errata/RHBA-2019:0327
- https://jenkins.io/security/advisory/2019-01-28/#SECURITY-1102
