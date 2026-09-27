# [H] CVE-2016-5157

## Summary
Severity: High
Advisory: CVE-2016-5157
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-09-11
Source: https://osv.dev/vulnerability/CVE-2016-5157
Type: osv

## Details
Heap-based buffer overflow in the opj_dwt_interleave_v function in dwt.c in OpenJPEG, as used in PDFium in Google Chrome before 53.0.2785.89 on Windows and OS X and before 53.0.2785.92 on Linux, allows remote attackers to execute arbitrary code via crafted coordinate values in JPEG 2000 data.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00008.html
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00073.html
- http://www.openwall.com/lists/oss-security/2016/09/08/5
- http://www.securityfocus.com/bid/92717
- http://www.securitytracker.com/id/1036729
- https://crbug.com/632622
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2T6IQAMS4W65MGP7UW5FPE22PXELTK5D/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/66BWMMMWXH32J5AOGLAJGZA3GH5LZHXH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AQ2IIIQSJ3J4MONBOGCG6XHLKKJX2HKM/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/H4IRSGYMBSHCBZP23CUDIRJ3LBKH6ZJ7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JYLOX7PZS3ZUHQ6RGI3M6H27B7I5ZZ26/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YGKSEWWWED77Q5ZHK4OA2EKSJXLRU3MK/
- https://pdfium.googlesource.com/pdfium/+/b6befb2ed2485a3805cddea86dc7574510178ea9
- http://rhn.redhat.com/errata/RHSA-2016-1854.html
- http://www.debian.org/security/2016/dsa-3660
- http://www.debian.org/security/2017/dsa-4013
- https://security.gentoo.org/glsa/201610-09
- https://bugzilla.redhat.com/show_bug.cgi?id=1374337
