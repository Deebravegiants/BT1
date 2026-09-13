# [M] JLSEC-2026-1224

## Summary
Severity: Medium
Advisory: JLSEC-2026-1224
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-08-09
Source: https://osv.dev/vulnerability/JLSEC-2026-1224
Type: osv

## Affected
- Julia: `Expat_jll` — affected >=0 <2.8.2+0

## Details
libexpat before 2.8.2 lacks handler call depth tracking for calls to `XML_GetBuffer`, `XML_Parse`, `XML_ParseBuffer`, `XML_ParserFree`, or `XML_ParserReset` from within handlers in cases of a policy violation. Thus, a use-after-free can occur,

## References
- https://github.com/libexpat/libexpat/pull/1246
