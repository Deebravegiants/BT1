# [M] ALPINE-CVE-2026-56412

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-56412
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-06-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-56412
Type: osv

## Affected
- Alpine:v3.21: `expat` — affected >=0 <2.8.2-r0
- Alpine:v3.22: `expat` — affected >=0 <2.8.2-r0
- Alpine:v3.23: `expat` — affected >=0 <2.8.2-r0
- Alpine:v3.24: `expat` — affected >=0 <2.8.2-r0

## Details
libexpat before 2.8.2 does not consider XML_TOK_DATA_CHARS in doCdataSection and thus lacks handler call depth tracking for various calls from within handlers in cases of a policy violation. Thus, a use-after-free can occur. NOTE: this issue exists because of an incomplete fix for CVE-2026-50219.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-56412
