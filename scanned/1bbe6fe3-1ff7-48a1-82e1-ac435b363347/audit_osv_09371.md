# [M] CVE-2016-9601

## Summary
Severity: Medium
Advisory: CVE-2016-9601
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2016-9601
Type: osv

## Details
ghostscript before version 9.21 is vulnerable to a heap based buffer overflow that was found in the ghostscript jbig2_decode_gray_scale_image function which is used to decode halftone segments in a JBIG2 image. A document (PostScript or PDF) with an embedded, specially crafted, jbig2 image could trigger a segmentation fault in ghostscript.

## References
- http://git.ghostscript.com/?p=jbig2dec.git%3Ba=commit%3Bh=e698d5c11d27212aa1098bc5b1673a3378563092
- http://www.securityfocus.com/bid/97095
- https://security.gentoo.org/glsa/201706-24
- https://www.debian.org/security/2017/dsa-3817
- https://bugs.ghostscript.com/show_bug.cgi?id=697457
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-9601
