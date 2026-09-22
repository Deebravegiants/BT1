# [M] JLSEC-2026-1225

## Summary
Severity: Medium
Advisory: JLSEC-2026-1225
Ecosystem: Julia
CVSS: 4.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-08-09
Source: https://osv.dev/vulnerability/JLSEC-2026-1225
Type: osv

## Affected
- Julia: `Expat_jll` — affected >=0 <2.8.2+0

## Details
libexpat before 2.8.2 lacks handler call depth tracking for calls to `XML_ResumeParser` from within handlers in cases of a policy violation. Thus, a use-after-free can occur (similar to the CVE-2026-50219 situation).

## References
- https://github.com/libexpat/libexpat/pull/1267
