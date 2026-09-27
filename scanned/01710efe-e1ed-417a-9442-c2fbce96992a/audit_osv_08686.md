# [H] CVE-2016-5314

## Summary
Severity: High
Advisory: CVE-2016-5314
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-12
Source: https://osv.dev/vulnerability/CVE-2016-5314
Type: osv

## Details
Buffer overflow in the PixarLogDecode function in tif_pixarlog.c in LibTIFF 4.0.6 and earlier allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted TIFF image, as demonstrated by overwriting the vgetparent function pointer with rgb2ycbcr.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00017.html
- http://lists.opensuse.org/opensuse-updates/2016-07/msg00087.html
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00060.html
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00090.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://www.securityfocus.com/bid/91195
- http://www.securityfocus.com/bid/91245
- https://security.gentoo.org/glsa/201701-16
- https://www.debian.org/security/2017/dsa-3762
- http://bugzilla.maptools.org/show_bug.cgi?id=2554
- https://bugzilla.redhat.com/show_bug.cgi?id=1346687
- https://github.com/vadz/libtiff/commit/391e77fcd217e78b2c51342ac3ddb7100ecacdd2
- http://www.openwall.com/lists/oss-security/2016/06/15/1
- http://www.openwall.com/lists/oss-security/2016/06/15/9
- http://www.openwall.com/lists/oss-security/2016/06/30/3
