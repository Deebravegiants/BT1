# [M] Jenkins Matrix Authorization Strategy Plugin: Unsafe deserialization allows invocation of parameterless constructors

## Summary
Severity: Medium
Advisory: GHSA-jp9r-mmhw-vff3
CVE: CVE-2026-42521
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-jp9r-mmhw-vff3
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:matrix-auth` — affected >=2.0-beta-1 <3.2.10

## Details
Jenkins Matrix Authorization Strategy Plugin 2.0-beta-1 through 3.2.9 (both inclusive) invokes parameterless constructors of classes specified in configuration when deserializing inheritance strategies, without restricting the classes that can be instantiated.

This can be abused by attackers with Item/Configure permission to instantiate arbitrary types, which may lead to information disclosure or other impacts depending on the classes available on the classpath.

Matrix Authorization Strategy Plugin 3.2.10 verifies that the class being instantiated is an inheritance strategy implementation, preventing instantiation of arbitrary types.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42521
- https://github.com/jenkinsci/matrix-auth-plugin
- https://www.jenkins.io/security/advisory/2026-04-29/#SECURITY-3676
