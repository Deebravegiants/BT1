# [M] CVE-2014-9655

## Summary
Severity: Medium
Advisory: CVE-2014-9655
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-04-13
Source: https://osv.dev/vulnerability/CVE-2014-9655
Type: osv

## Details
The (1) putcontig8bitYCbCr21tile function in tif_getimage.c or (2) NeXTDecode function in tif_next.c in LibTIFF allows remote attackers to cause a denial of service (uninitialized memory access) via a crafted TIFF image, as demonstrated by libtiff-cvs-1.tif and libtiff-cvs-2.tif.

## References
- http://rhn.redhat.com/errata/RHSA-2016-1546.html
- http://rhn.redhat.com/errata/RHSA-2016-1547.html
- http://www.debian.org/security/2015/dsa-3273
- http://www.debian.org/security/2016/dsa-3467
- https://security.gentoo.org/glsa/201701-16
- http://openwall.com/lists/oss-security/2015/02/07/5
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
