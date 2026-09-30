# [H] CVE-2016-5158

## Summary
Severity: High
Advisory: CVE-2016-5158
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-09-11
Source: https://osv.dev/vulnerability/CVE-2016-5158
Type: osv

## Details
Multiple integer overflows in the opj_tcd_init_tile function in tcd.c in OpenJPEG, as used in PDFium in Google Chrome before 53.0.2785.89 on Windows and OS X and before 53.0.2785.92 on Linux, allow remote attackers to cause a denial of service (heap-based buffer overflow) or possibly have unspecified other impact via crafted JPEG 2000 data.

## References
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00073.html
- http://www.securitytracker.com/id/1036729
- https://crbug.com/628890
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00003.html
- http://www.securityfocus.com/bid/92717
- https://pdfium.googlesource.com/pdfium.git/+/ff74356915d4c7f7c6eb16de1e9f403da4ecb6d5
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00008.html
- http://rhn.redhat.com/errata/RHSA-2017-0559.html
- http://www.debian.org/security/2016/dsa-3660
- http://rhn.redhat.com/errata/RHSA-2016-1854.html
- http://rhn.redhat.com/errata/RHSA-2017-0838.html
- https://security.gentoo.org/glsa/201610-09
- https://googlechromereleases.blogspot.com/2016/08/stable-channel-update-for-desktop_31.html
