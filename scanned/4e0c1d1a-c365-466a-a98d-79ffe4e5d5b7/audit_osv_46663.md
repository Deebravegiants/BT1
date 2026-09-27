# [M] CVE-2014-8127

## Summary
Severity: Medium
Advisory: CVE-2014-8127
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-26
Source: https://osv.dev/vulnerability/CVE-2014-8127
Type: osv

## Details
LibTIFF 4.0.3 allows remote attackers to cause a denial of service (out-of-bounds read and crash) via a crafted TIFF image to the (1) checkInkNamesString function in tif_dir.c in the thumbnail tool, (2) compresscontig function in tiff2bw.c in the tiff2bw tool, (3) putcontig8bitCIELab function in tif_getimage.c in the tiff2rgba tool, LZWPreDecode function in tif_lzw.c in the (4) tiff2ps or (5) tiffdither tool, (6) NeXTDecode function in tif_next.c in the tiffmedian tool, or (7) TIFFWriteDirectoryTagLongLong8Array function in tif_dirwrite.c in the tiffset tool.

## References
- http://lists.opensuse.org/opensuse-updates/2015-03/msg00022.html
- http://rhn.redhat.com/errata/RHSA-2016-1546.html
- http://rhn.redhat.com/errata/RHSA-2016-1547.html
- http://www.conostix.com/pub/adv/CVE-2014-8127-LibTIFF-Out-of-bounds_Reads.txt
- http://www.debian.org/security/2015/dsa-3273
- http://www.openwall.com/lists/oss-security/2015/01/24/15
- http://www.securityfocus.com/bid/72323
- https://security.gentoo.org/glsa/201701-16
- http://www.openwall.com/lists/oss-security/2015/01/24/15
- http://bugzilla.maptools.org/show_bug.cgi?id=2484
- http://bugzilla.maptools.org/show_bug.cgi?id=2485
- http://bugzilla.maptools.org/show_bug.cgi?id=2486
- http://bugzilla.maptools.org/show_bug.cgi?id=2496
- http://bugzilla.maptools.org/show_bug.cgi?id=2497
- http://bugzilla.maptools.org/show_bug.cgi?id=2500
- http://www.securitytracker.com/id/1032760
