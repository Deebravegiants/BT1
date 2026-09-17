# [H] CVE-2016-5152

## Summary
Severity: High
Advisory: CVE-2016-5152
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-09-11
Source: https://osv.dev/vulnerability/CVE-2016-5152
Type: osv

## Details
Integer overflow in the opj_tcd_get_decoded_tile_size function in tcd.c in OpenJPEG, as used in PDFium in Google Chrome before 53.0.2785.89 on Windows and OS X and before 53.0.2785.92 on Linux, allows remote attackers to cause a denial of service (heap-based buffer overflow) or possibly have unspecified other impact via crafted JPEG 2000 data.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00004.html
- http://www.securityfocus.com/bid/92717
- https://codereview.chromium.org/2182683002
- https://crbug.com/629919
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00008.html
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00073.html
- http://www.securitytracker.com/id/1036729
- http://rhn.redhat.com/errata/RHSA-2016-1854.html
- http://www.debian.org/security/2017/dsa-4013
- https://security.gentoo.org/glsa/201610-09
- http://www.debian.org/security/2016/dsa-3660
- https://googlechromereleases.blogspot.com/2016/08/stable-channel-update-for-desktop_31.html
