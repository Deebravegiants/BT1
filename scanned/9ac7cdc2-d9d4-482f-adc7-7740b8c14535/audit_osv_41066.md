# [H] CVE-2026-57280

## Summary
Severity: High
Advisory: CVE-2026-57280
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-57280
Type: osv

## Details
Jenkins Script Security Plugin 1402.v94c9ce464861 and earlier does not intercept the implicit type casts applied to the elements of typed for-each loops in sandboxed Groovy scripts, allowing attackers able to provide such scripts to invoke arbitrary constructors and bypass the sandbox protection.

## References
- https://www.jenkins.io/security/advisory/2026-06-24/#SECURITY-3792
