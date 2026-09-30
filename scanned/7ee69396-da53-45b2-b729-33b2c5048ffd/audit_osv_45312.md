# [C] An issue was discovered in libexpat before 2.6.3

## Summary
Severity: Critical
Advisory: JLSEC-2025-63
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-14
Source: https://osv.dev/vulnerability/JLSEC-2025-63
Type: osv

## Affected
- Julia: `Expat_jll` — affected >=0 <2.6.4+0

## Details
An issue was discovered in libexpat before 2.6.3. dtdCopy in xmlparse.c can have an integer overflow for nDefaultAtts on 32-bit platforms (where `UINT_MAX` equals `SIZE_MAX`).

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://github.com/libexpat/libexpat/issues/888
- https://github.com/libexpat/libexpat/pull/891
- https://lists.debian.org/debian-lts-announce/2024/09/msg00036.html
- https://security.netapp.com/advisory/ntap-20241018-0003/
