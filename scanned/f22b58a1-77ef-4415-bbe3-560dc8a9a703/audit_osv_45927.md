# [M] JLSEC-2026-483

## Summary
Severity: Medium
Advisory: JLSEC-2026-483
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-483
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.1.0+0

## Details
Buffer Overflow in LibTiff v4.0.10 allows attackers to cause a denial of service via the 'in `_TIFFmemcpy`' funtion in the component '`tif_unix.c`'.

## References
- http://bugzilla.maptools.org/show_bug.cgi?id=2852
- https://gitlab.com/libtiff/libtiff/-/issues/159
- https://lists.debian.org/debian-lts-announce/2021/10/msg00004.html
- https://security.netapp.com/advisory/ntap-20211004-0005/
