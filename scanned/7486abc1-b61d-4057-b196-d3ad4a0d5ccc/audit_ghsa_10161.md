# [M] Jenkins GitHub Branch Source Plugin: Missing permissions check allows attackers to perform a connection test

## Summary
Severity: Medium
Advisory: GHSA-wg26-8wmj-cf9p
CVE: CVE-2026-42522
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-wg26-8wmj-cf9p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:github-branch-source` — affected >=0 <1967.1969.v205fd594c821

## Details
Jenkins GitHub Branch Source Plugin versions 1967.vdea_d580c1a_b_a_ and earlier do not perform a permission check in a method implementing form validation.

This allows attackers with Overall/Read permission to connect to an attacker-specified URL with attacker-specified GitHub App credentials.

GitHub Branch Source Plugin 1967.1969.v205fd594c821 requires Overall/Manage permission to perform the connection test.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42522
- https://www.jenkins.io/security/advisory/2026-04-29/#SECURITY-3702
