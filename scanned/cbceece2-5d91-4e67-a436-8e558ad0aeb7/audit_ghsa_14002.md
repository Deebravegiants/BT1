# [H] Jenkins File Parameter Plugin arbitrary file write vulnerability

## Summary
Severity: High
Advisory: GHSA-46f2-x6h2-x9hx
CVE: CVE-2023-32986
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-16
Source: https://github.com/advisories/GHSA-46f2-x6h2-x9hx
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:file-parameters` — affected >=0 <285.287.v4b

## Details
Jenkins File Parameter Plugin 285.v757c5b_67a_c25 and earlier does not restrict the name (and resulting uploaded file name) of Stashed File Parameters.

This allows attackers with Item/Configure permission to create or replace arbitrary files on the Jenkins controller file system with attacker-specified content.

File Parameter Plugin 285.287.v4b_7b_29d3469d restricts the name (and resulting uploaded file name) of Stashed File Parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32986
- https://github.com/jenkinsci/file-parameters-plugin/commit/4b7b29d3469dc020ec61a387c0c793c1f1ac31dd
- https://www.jenkins.io/security/advisory/2023-05-16/#SECURITY-3123
