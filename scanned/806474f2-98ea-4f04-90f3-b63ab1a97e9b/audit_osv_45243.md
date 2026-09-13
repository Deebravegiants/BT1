# [M] An Invalid Address dereference was discovered in TIFFWriteDirectoryTagTransferfunction in...

## Summary
Severity: Medium
Advisory: JLSEC-2025-252
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-252
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=0 <4.1.0+0

## Details
An Invalid Address dereference was discovered in TIFFWriteDirectoryTagTransferfunction in `libtiff/tif_dirwrite.c` in LibTIFF 4.0.10, affecting the cpSeparateBufToContigBuf function in tiffcp.c. Remote attackers could leverage this vulnerability to cause a denial-of-service via a crafted tiff file. This is different from CVE-2018-12900.

## References
- http://bugzilla.maptools.org/show_bug.cgi?id=2833
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00041.html
- https://gitlab.com/libtiff/libtiff/commit/802d3cbf3043be5dce5317e140ccb1c17a6a2d39
- https://lists.debian.org/debian-lts-announce/2019/02/msg00026.html
- https://security.gentoo.org/glsa/202003-25
- https://usn.ubuntu.com/3906-1/
- https://usn.ubuntu.com/3906-2/
- https://www.debian.org/security/2020/dsa-4670
