# [H] CVE-2016-9453

## Summary
Severity: High
Advisory: CVE-2016-9453
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/CVE-2016-9453
Type: osv

## Details
The t2p_readwrite_pdf_image_tile function in LibTIFF allows remote attackers to cause a denial of service (out-of-bounds write and crash) or possibly execute arbitrary code via a JPEG file with a TIFFTAG_JPEGTABLES of length one.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-12/msg00017.html
- http://www.debian.org/security/2017/dsa-3762
- http://www.openwall.com/lists/oss-security/2016/11/19/1
- http://www.securityfocus.com/bid/94406
- https://security.gentoo.org/glsa/201701-16
- http://bugzilla.maptools.org/show_bug.cgi?id=2579
