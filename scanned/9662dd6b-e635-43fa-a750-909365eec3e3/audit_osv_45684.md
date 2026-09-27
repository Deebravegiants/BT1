# [M] JLSEC-2026-200

## Summary
Severity: Medium
Advisory: JLSEC-2026-200
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-200
Type: osv

## Affected
- Julia: `NASM_jll` — affected >=0 <2.16.1+0

## Details
A Segmentation Fault issue discovered in in `ieee_segment` function in outieee.c in nasm 2.14.03 and 2.15 allows remote attackers to cause a denial of service via crafted assembly file.

## References
- https://bugzilla.nasm.us/show_bug.cgi?id=3392637
- https://security.gentoo.org/glsa/202312-09
