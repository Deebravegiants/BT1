# [C] CVE-2015-8668

## Summary
Severity: Critical
Advisory: CVE-2015-8668
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-01-08
Source: https://osv.dev/vulnerability/CVE-2015-8668
Type: osv

## Details
Heap-based buffer overflow in the PackBitsPreEncode function in tif_packbits.c in bmp2tiff in libtiff 4.0.6 and earlier allows remote attackers to execute arbitrary code or cause a denial of service via a large width field in a BMP image.

## References
- http://packetstormsecurity.com/files/135080/libtiff-4.0.6-Heap-Overflow.html
- http://rhn.redhat.com/errata/RHSA-2016-1546.html
- http://rhn.redhat.com/errata/RHSA-2016-1547.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinjul2016-3090546.html
- http://www.securityfocus.com/archive/1/537208/100/0/threaded
- https://security.gentoo.org/glsa/201701-16
- http://packetstormsecurity.com/files/135080/libtiff-4.0.6-Heap-Overflow.html
- http://www.securityfocus.com/archive/1/537208/100/0/threaded
