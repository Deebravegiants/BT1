# [M] Missing permission check in Perfecto Plugin

## Summary
Severity: Medium
Advisory: GHSA-3h2q-m63q-9cf6
CVE: CVE-2020-2260
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3h2q-m63q-9cf6
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:perfecto` — affected >=0 <1.18

## Details
Perfecto Plugin 1.17 and earlier does not perform a permission check in a method implementing a connection test.

This allows attackers with Overall/Read permission to connect to an attacker-specified HTTP URL using attacker-specified username and password.

Perfecto Plugin 1.18 requires Overall/Administer permission to perform a connection test.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2260
- https://github.com/jenkinsci/perfecto-plugin
- https://www.jenkins.io/security/advisory/2020-09-16/#SECURITY-1979
- http://www.openwall.com/lists/oss-security/2020/09/16/3
