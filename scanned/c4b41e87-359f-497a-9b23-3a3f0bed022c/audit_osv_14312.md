# [H] CVE-2018-8905

## Summary
Severity: High
Advisory: CVE-2018-8905
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-22
Source: https://osv.dev/vulnerability/CVE-2018-8905
Type: osv

## Details
In LibTIFF 4.0.9, a heap-based buffer overflow occurs in the function LZWDecodeCompat in tif_lzw.c via a crafted TIFF file, as demonstrated by tiff2ps.

## References
- https://access.redhat.com/errata/RHSA-2019:2053
- https://lists.debian.org/debian-lts-announce/2018/05/msg00008.html
- https://lists.debian.org/debian-lts-announce/2018/05/msg00009.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00002.html
- https://usn.ubuntu.com/3864-1/
- https://www.debian.org/security/2018/dsa-4349
- http://bugzilla.maptools.org/show_bug.cgi?id=2780
- https://gitlab.com/libtiff/libtiff/commit/58a898cb4459055bb488ca815c23b880c242a27d
- https://github.com/halfbitteam/POCs/tree/master/libtiff-4.08_tiff2ps_heap_overflow
