# [M] CVE-2019-7663

## Summary
Severity: Medium
Advisory: CVE-2019-7663
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-09
Source: https://osv.dev/vulnerability/CVE-2019-7663
Type: osv

## Details
An Invalid Address dereference was discovered in TIFFWriteDirectoryTagTransferfunction in libtiff/tif_dirwrite.c in LibTIFF 4.0.10, affecting the cpSeparateBufToContigBuf function in tiffcp.c. Remote attackers could leverage this vulnerability to cause a denial-of-service via a crafted tiff file. This is different from CVE-2018-12900.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00041.html
- https://lists.debian.org/debian-lts-announce/2019/02/msg00026.html
- https://security.gentoo.org/glsa/202003-25
- https://usn.ubuntu.com/3906-1/
- https://usn.ubuntu.com/3906-2/
- https://www.debian.org/security/2020/dsa-4670
- http://bugzilla.maptools.org/show_bug.cgi?id=2833
- https://gitlab.com/libtiff/libtiff/commit/802d3cbf3043be5dce5317e140ccb1c17a6a2d39
