# [C] ALPINE-CVE-2026-39892

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-39892
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-39892
Type: osv

## Affected
- Alpine:v3.23: `py3-cryptography` — affected >=45.0.0 <46.0.7-r0
- Alpine:v3.24: `py3-cryptography` — affected >=45.0.0 <46.0.7-r0

## Details
cryptography is a package designed to expose cryptographic primitives and recipes to Python developers. From 45.0.0 to before 46.0.7, if a non-contiguous buffer was passed to APIs which accepted Python buffers (e.g. Hash.update()), this could lead to buffer overflows. This vulnerability is fixed in 46.0.7.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-39892
