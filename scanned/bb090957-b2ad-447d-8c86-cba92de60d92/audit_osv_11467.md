# [H] CVE-2017-7975

## Summary
Severity: High
Advisory: CVE-2017-7975
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-19
Source: https://osv.dev/vulnerability/CVE-2017-7975
Type: osv

## Details
Artifex jbig2dec 0.13, as used in Ghostscript, allows out-of-bounds writes because of an integer overflow in the jbig2_build_huffman_table function in jbig2_huffman.c during operations on a crafted JBIG2 file, leading to a denial of service (application crash) or possibly execution of arbitrary code.

## References
- http://www.debian.org/security/2017/dsa-3855
- https://security.gentoo.org/glsa/201708-10
- https://bugs.ghostscript.com/show_bug.cgi?id=697693
