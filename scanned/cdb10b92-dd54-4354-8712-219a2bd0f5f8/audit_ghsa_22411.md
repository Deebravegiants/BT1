# [M] Jenkins Build Environment Plugin vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-88qj-3q6h-8m5q
CVE: CVE-2019-10395
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-88qj-3q6h-8m5q
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:build-environment` — affected >=0 <1.7

## Details
Build Environment Plugin did not escape values of environment variables shown on its views. This resulted in a cross-site scripting vulnerability exploitable by attackers able to control the values of build environment variables, typically users with Job/Configure or Job/Build permission.

Jenkins applies the missing escaping by default since 2.146 and LTS 2.138.2, so newer Jenkins releases are not affected by this vulnerability.

Build Environment Plugin now escapes all variables displayed in its views.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10395
- https://github.com/jenkinsci/build-environment-plugin/commit/c9797608e839d0dce1957e3c1b512b872839e603
- https://jenkins.io/security/advisory/2019-09-12/#SECURITY-1476
- http://www.openwall.com/lists/oss-security/2019/09/12/2
