# [M] JLSEC-2026-378

## Summary
Severity: Medium
Advisory: JLSEC-2026-378
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/JLSEC-2026-378
Type: osv

## Affected
- Julia: `Expat_jll` — affected >=0 <2.7.5+0

## Details
In libexpat through 2.7.3, a crafted file with an approximate size of 2 MiB can lead to dozens of seconds of processing time.

## References
- http://www.openwall.com/lists/oss-security/2025/12/02/1
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://github.com/libexpat/libexpat/issues/1076
