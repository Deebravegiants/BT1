# [H] CVE-2017-7246

## Summary
Severity: High
Advisory: CVE-2017-7246
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2017-7246
Type: osv

## Details
Stack-based buffer overflow in the pcre32_copy_substring function in pcre_get.c in libpcre1 in PCRE 8.40 allows remote attackers to cause a denial of service (WRITE of size 268) or possibly have unspecified other impact via a crafted file.

## References
- https://access.redhat.com/errata/RHSA-2018:2486
- https://blogs.gentoo.org/ago/2017/03/20/libpcre-two-stack-based-buffer-overflow-write-in-pcre32_copy_substring-pcre_get-c/
- https://security.gentoo.org/glsa/201710-25
- http://www.securityfocus.com/bid/97067
