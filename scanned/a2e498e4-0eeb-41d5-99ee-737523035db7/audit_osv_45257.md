# [M] A vulnerability classified as problematic was found in LibTIFF 4.3.0

## Summary
Severity: Medium
Advisory: JLSEC-2025-268
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-268
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=4.3.0+0 <4.4.0+0

## Details
A vulnerability classified as problematic was found in LibTIFF 4.3.0. Affected by this vulnerability is the TIFF File Handler of tiff2ps. Opening a malicious file leads to a denial of service. The attack can be launched remotely but requires user interaction. The exploit has been disclosed to the public and may be used.

## References
- https://gitlab.com/libtiff/libtiff/-/issues/402
- https://gitlab.com/libtiff/libtiff/uploads/c3da94e53cf1e1e8e6d4d3780dc8c42f/example.tiff
- https://security.gentoo.org/glsa/202210-10
- https://security.netapp.com/advisory/ntap-20220513-0005/
- https://vuldb.com/?id.196363
