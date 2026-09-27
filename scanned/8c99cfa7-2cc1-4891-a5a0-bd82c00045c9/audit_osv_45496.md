# [M] JLSEC-2026-1236

## Summary
Severity: Medium
Advisory: JLSEC-2026-1236
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-08-09
Source: https://osv.dev/vulnerability/JLSEC-2026-1236
Type: osv

## Affected
- Julia: `Expat_jll` — affected >=0 <2.8.2+0

## Details
libexpat before 2.8.2 does not consider `XML_TOK_DATA_CHARS` in doCdataSection and thus lacks handler call depth tracking for various calls from within handlers in cases of a policy violation. Thus, a use-after-free can occur. NOTE: this issue exists because of an incomplete fix for CVE-2026-50219.

## References
- https://github.com/libexpat/libexpat/pull/1278
