# [M] ALPINE-CVE-2025-48386

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-48386
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2025-07-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-48386
Type: osv

## Affected
- Alpine:v3.19: `git` — affected >=0 <2.43.7-r0
- Alpine:v3.20: `git` — affected >=0 <2.45.4-r0
- Alpine:v3.21: `git` — affected >=0 <2.47.3-r0
- Alpine:v3.22: `git` — affected >=0 <2.49.1-r0
- Alpine:v3.23: `git` — affected >=0 <2.50.1-r0
- Alpine:v3.24: `git` — affected >=0 <2.50.1-r0

## Details
Git is a fast, scalable, distributed revision control system with an unusually rich command set that provides both high-level operations and full access to internals. The wincred credential helper uses a static buffer (target) as a unique key for storing and comparing against internal storage. This credential helper does not properly bounds check the available space remaining in the buffer before appending to it with wcsncat(), leading to potential buffer overflows. This vulnerability is fixed in v2.43.7, v2.44.4, v2.45.4, v2.46.4, v2.47.3, v2.48.2, v2.49.1, and v2.50.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-48386
