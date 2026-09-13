# [M] Jenkins Script Security Plugin: Missing permission checks allow enumeration of pending and approved classpaths 

## Summary
Severity: Medium
Advisory: GHSA-p334-gfhq-c7w6
CVE: CVE-2026-42519
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-p334-gfhq-c7w6
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1402.v94c9ce464861

## Details
Jenkins Script Security Plugin versions 1399.ve6a_66547f6e1 and earlier do not perform a permission check in an HTTP endpoint.

This allows attackers with Overall/Read permission to enumerate pending and approved Script Security classpaths.

Script Security Plugin 1402.v94c9ce464861 requires Overall/Administer permission to enumerate pending and approved Script Security classpaths.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42519
- https://github.com/jenkinsci/script-security-plugin
- https://www.jenkins.io/security/advisory/2026-04-29/#SECURITY-3662
