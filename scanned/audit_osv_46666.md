# [M] CVE-2014-8130

## Summary
Severity: Medium
Advisory: CVE-2014-8130
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-12
Source: https://osv.dev/vulnerability/CVE-2014-8130
Type: osv

## Details
The _TIFFmalloc function in tif_unix.c in LibTIFF 4.0.3 does not reject a zero size, which allows remote attackers to cause a denial of service (divide-by-zero error and application crash) via a crafted TIFF image that is mishandled by the TIFFWriteScanline function in tif_write.c, as demonstrated by tiffdither.

## References
- http://lists.apple.com/archives/security-announce/2015/Jun/msg00001.html
- http://lists.apple.com/archives/security-announce/2015/Jun/msg00002.html
- http://rhn.redhat.com/errata/RHSA-2016-1546.html
- http://rhn.redhat.com/errata/RHSA-2016-1547.html
- http://support.apple.com/kb/HT204941
- http://support.apple.com/kb/HT204942
- http://www.conostix.com/pub/adv/CVE-2014-8130-LibTIFF-Division_By_Zero.txt
- http://www.securityfocus.com/bid/72353
- http://www.securitytracker.com/id/1032760
- https://security.gentoo.org/glsa/201701-16
- http://lists.apple.com/archives/security-announce/2015/Jun/msg00001.html
- http://lists.apple.com/archives/security-announce/2015/Jun/msg00002.html
- http://openwall.com/lists/oss-security/2015/01/24/15
- http://bugzilla.maptools.org/show_bug.cgi?id=2483
- https://bugzilla.redhat.com/show_bug.cgi?id=1185817
- https://github.com/vadz/libtiff/commit/3c5eb8b1be544e41d2c336191bc4936300ad7543
- http://bugzilla.maptools.org/show_bug.cgi?id=2483
- https://bugzilla.redhat.com/show_bug.cgi?id=1185817
