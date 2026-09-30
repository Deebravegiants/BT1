# [H] CVE-2014-8129

## Summary
Severity: High
Advisory: CVE-2014-8129
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-12
Source: https://osv.dev/vulnerability/CVE-2014-8129
Type: osv

## Details
LibTIFF 4.0.3 allows remote attackers to cause a denial of service (out-of-bounds write) or possibly have unspecified other impact via a crafted TIFF image, as demonstrated by failure of tif_next.c to verify that the BitsPerSample value is 2, and the t2p_sample_lab_signed_to_unsigned function in tiff2pdf.c.

## References
- http://rhn.redhat.com/errata/RHSA-2016-1546.html
- http://rhn.redhat.com/errata/RHSA-2016-1547.html
- http://support.apple.com/kb/HT204941
- http://support.apple.com/kb/HT204942
- http://www.conostix.com/pub/adv/CVE-2014-8129-LibTIFF-Out-of-bounds_Reads_and_Writes.txt
- http://www.securityfocus.com/bid/72352
- http://www.securitytracker.com/id/1032760
- https://security.gentoo.org/glsa/201701-16
- https://www.debian.org/security/2015/dsa-3273
- http://lists.apple.com/archives/security-announce/2015/Jun/msg00001.html
- http://lists.apple.com/archives/security-announce/2015/Jun/msg00002.html
- http://openwall.com/lists/oss-security/2015/01/24/15
- http://bugzilla.maptools.org/show_bug.cgi?id=2487
- http://bugzilla.maptools.org/show_bug.cgi?id=2488
- https://bugzilla.redhat.com/show_bug.cgi?id=1185815
- http://bugzilla.maptools.org/show_bug.cgi?id=2487
- http://bugzilla.maptools.org/show_bug.cgi?id=2488
- https://bugzilla.redhat.com/show_bug.cgi?id=1185815
