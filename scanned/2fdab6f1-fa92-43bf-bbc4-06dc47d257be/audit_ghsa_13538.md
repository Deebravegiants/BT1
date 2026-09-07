# [H] Stored XSS vulnerability in Jenkins GitHub Plugin

## Summary
Severity: High
Advisory: GHSA-mv77-fj63-q5w8
CVE: CVE-2023-46650
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-mv77-fj63-q5w8
Type: github-advisory

## Affected
- Maven: `com.coravy.hudson.plugins.github:github` — affected >=0 <1.37.3.1

## Details
Jenkins GitHub Plugin 1.37.3 and earlier does not escape the GitHub project URL on the build page when showing changes.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

GitHub Plugin 1.37.3.1 escapes GitHub project URL on the build page when showing changes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46650
- https://github.com/jenkinsci/github-plugin/commit/9e09678c445613521c45acce0ce525160747ff3e
- https://github.com/jenkinsci/github-plugin
- https://www.jenkins.io/security/advisory/2023-10-25/#SECURITY-3246
- http://www.openwall.com/lists/oss-security/2023/10/25/2
