# [H] CVE-2017-7885

## Summary
Severity: High
Advisory: CVE-2017-7885
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2017-04-17
Source: https://osv.dev/vulnerability/CVE-2017-7885
Type: osv

## Details
Artifex jbig2dec 0.13 has a heap-based buffer over-read leading to denial of service (application crash) or disclosure of sensitive information from process memory, because of an integer overflow in the jbig2_decode_symbol_dict function in jbig2_symbol_dict.c in libjbig2dec.a during operation on a crafted .jb2 file.

## References
- http://www.debian.org/security/2017/dsa-3855
- https://security.gentoo.org/glsa/201708-10
- https://bugs.ghostscript.com/show_bug.cgi?id=697703
