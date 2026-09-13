# [M] CVE-2018-7456

## Summary
Severity: Medium
Advisory: CVE-2018-7456
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-24
Source: https://osv.dev/vulnerability/CVE-2018-7456
Type: osv

## Details
A NULL Pointer Dereference occurs in the function TIFFPrintDirectory in tif_print.c in LibTIFF 3.9.3, 3.9.4, 3.9.5, 3.9.6, 3.9.7, 4.0.0alpha4, 4.0.0alpha5, 4.0.0alpha6, 4.0.0beta7, 4.0.0, 4.0.1, 4.0.2, 4.0.3, 4.0.4, 4.0.4beta, 4.0.5, 4.0.6, 4.0.7, 4.0.8 and 4.0.9 when using the tiffinfo tool to print crafted TIFF information, a different vulnerability than CVE-2017-18013. (This affects an earlier part of the TIFFPrintDirectory function that was not addressed by the CVE-2017-18013 patch.)

## References
- https://access.redhat.com/errata/RHSA-2019:2051
- https://access.redhat.com/errata/RHSA-2019:2053
- https://lists.debian.org/debian-lts-announce/2018/04/msg00010.html
- https://lists.debian.org/debian-lts-announce/2018/04/msg00011.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00002.html
- https://usn.ubuntu.com/3864-1/
- https://www.debian.org/security/2018/dsa-4349
- http://bugzilla.maptools.org/show_bug.cgi?id=2778
- https://gitlab.com/libtiff/libtiff/commit/be4c85b16e8801a16eec25e80eb9f3dd6a96731b
- https://github.com/xiaoqx/pocs/tree/master/libtiff
