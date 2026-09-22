# [M] JLSEC-2026-1230

## Summary
Severity: Medium
Advisory: JLSEC-2026-1230
Ecosystem: Julia
CVSS: 6.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-08-09
Source: https://osv.dev/vulnerability/JLSEC-2026-1230
Type: osv

## Affected
- Julia: `Expat_jll` — affected >=0 <2.8.2+0

## Details
libexpat before 2.8.2 has an integer overflow in `XML_ParseBuffer` because it lacked a check that was present in `XML_Parse`.

## References
- https://github.com/libexpat/libexpat/pull/1255
