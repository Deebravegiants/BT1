# [H] Yarn untrusted search path vulnerability

## Summary
Severity: High
Advisory: GHSA-mpwj-fcr6-x34c
CVE: CVE-2021-4435
CWE: CWE-426
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-04
Source: https://github.com/advisories/GHSA-mpwj-fcr6-x34c
Type: github-advisory

## Affected
- npm: `yarn` — affected >=0 <1.22.13

## Details
An untrusted search path vulnerability was found in Yarn. When a victim runs certain Yarn commands in a directory with attacker-controlled content, malicious commands could be executed in unexpected ways.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4435
- https://github.com/yarnpkg/yarn/commit/67fcce88935e45092ffa2674c08053f1ef5268a1
- https://access.redhat.com/security/cve/CVE-2021-4435
- https://bugzilla.redhat.com/show_bug.cgi?id=2262284
- https://github.com/yarnpkg/yarn
- https://github.com/yarnpkg/yarn/releases/tag/v1.22.13
