# [M] JLSEC-2026-383

## Summary
Severity: Medium
Advisory: JLSEC-2026-383
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/JLSEC-2026-383
Type: osv

## Affected
- Julia: `Expat_jll` — affected >=0 <2.7.5+0

## Details
libexpat before 2.7.5 allows a NULL pointer dereference in the function setContext on retry after an earlier ouf-of-memory condition.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://github.com/libexpat/libexpat/pull/1159
- https://github.com/libexpat/libexpat/pull/1163
