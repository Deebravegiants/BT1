# [H] CVE-2017-7976

## Summary
Severity: High
Advisory: CVE-2017-7976
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2017-04-19
Source: https://osv.dev/vulnerability/CVE-2017-7976
Type: osv

## Details
Artifex jbig2dec 0.13 allows out-of-bounds writes and reads because of an integer overflow in the jbig2_image_compose function in jbig2_image.c during operations on a crafted .jb2 file, leading to a denial of service (application crash) or disclosure of sensitive information from process memory.

## References
- http://www.debian.org/security/2017/dsa-3855
- https://security.gentoo.org/glsa/201708-10
- https://bugs.ghostscript.com/show_bug.cgi?id=697683
