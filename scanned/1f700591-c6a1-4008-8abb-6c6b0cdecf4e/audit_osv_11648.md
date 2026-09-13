# [M] CVE-2017-9216

## Summary
Severity: Medium
Advisory: CVE-2017-9216
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-24
Source: https://osv.dev/vulnerability/CVE-2017-9216
Type: osv

## Details
libjbig2dec.a in Artifex jbig2dec 0.13, as used in MuPDF and Ghostscript, has a NULL pointer dereference in the jbig2_huffman_get function in jbig2_huffman.c. For example, the jbig2dec utility will crash (segmentation fault) when parsing an invalid file.

## References
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=3ebffb1d96ba0cacec23016eccb4047dab365853
- http://www.securityfocus.com/bid/98680
- https://lists.debian.org/debian-lts-announce/2021/10/msg00023.html
- https://bugs.ghostscript.com/show_bug.cgi?id=697934
