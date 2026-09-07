# [H] Reflected Cross-site Scripting in Jenkins Nested View Plugin

## Summary
Severity: High
Advisory: GHSA-h642-5h74-3x9c
CVE: CVE-2022-34182
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-h642-5h74-3x9c
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:nested-view` — affected >=1.20 <1.26

## Details
Jenkins Nested View Plugin 1.20 through 1.25 (both inclusive) does not escape search parameters, resulting in a reflected cross-site scripting (XSS) vulnerability.

Nested View Plugin 1.26 escapes search parameters

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34182
- https://github.com/jenkinsci/nested-view-plugin/commit/00505d69939bc45574ff27eecc06e997857e5bf6
- https://github.com/jenkinsci/nested-view-plugin
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2768
