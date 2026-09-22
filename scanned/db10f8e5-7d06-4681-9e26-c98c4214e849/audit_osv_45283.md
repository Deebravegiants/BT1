# [M] There exists one heap buffer overflow in `_TIFFmemcpy` in `tif_unix.c` in libtiff 4.0.10, which...

## Summary
Severity: Medium
Advisory: JLSEC-2025-309
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-309
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.1.0+0

## Details
There exists one heap buffer overflow in `_TIFFmemcpy` in `tif_unix.c` in libtiff 4.0.10, which allows an attacker to cause a denial-of-service through a crafted tiff file.

## References
- http://bugzilla.maptools.org/show_bug.cgi?id=2848
