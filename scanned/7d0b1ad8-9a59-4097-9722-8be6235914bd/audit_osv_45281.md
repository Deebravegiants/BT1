# [M] A NULL pointer dereference flaw was found in Libtiff's LZWDecode() function in the...

## Summary
Severity: Medium
Advisory: JLSEC-2025-303
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-303
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.5.1+0

## Details
A NULL pointer dereference flaw was found in Libtiff's LZWDecode() function in the `libtiff/tif_lzw.c` file. This flaw allows a local attacker to craft specific input data that can cause the program to dereference a NULL pointer when decompressing a TIFF format file, resulting in a program crash or denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2023-2731
- https://bugzilla.redhat.com/show_bug.cgi?id=2207635
- https://github.com/libsdl-org/libtiff/commit/9be22b639ea69e102d3847dca4c53ef025e9527b
- https://gitlab.com/libtiff/libtiff/-/issues/548
- https://security.netapp.com/advisory/ntap-20230703-0009/
