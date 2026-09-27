# [M] Git allows a buffer overflow in 'wincred' credential helper

## Summary
Severity: Medium
Advisory: BIT-git-2025-48386
Aliases: CVE-2025-48386, GHSA-4v56-3xvj-xvfr
Ecosystem: Bitnami
Published: 2025-07-10
Source: https://osv.dev/vulnerability/BIT-git-2025-48386
Type: osv

## Affected
- Bitnami: `git` — affected >=0 <2.50.1

## Details
Git is a fast, scalable, distributed revision control system with an unusually rich command set that provides both high-level operations and full access to internals. The wincred credential helper uses a static buffer (target) as a unique key for storing and comparing against internal storage. This credential helper does not properly bounds check the available space remaining in the buffer before appending to it with wcsncat(), leading to potential buffer overflows. This vulnerability is fixed in v2.43.7, v2.44.4, v2.45.4, v2.46.4, v2.47.3, v2.48.2, v2.49.1, and v2.50.1.

## References
- https://github.com/git/git/security/advisories/GHSA-4v56-3xvj-xvfr
- https://nvd.nist.gov/vuln/detail/CVE-2025-48386
- http://www.openwall.com/lists/oss-security/2025/07/08/4
