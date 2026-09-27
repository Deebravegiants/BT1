# [M] CVE-2017-7244

## Summary
Severity: Medium
Advisory: CVE-2017-7244
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2017-7244
Type: osv

## Details
The _pcre32_xclass function in pcre_xclass.c in libpcre1 in PCRE 8.40 allows remote attackers to cause a denial of service (invalid memory read) via a crafted file.

## References
- https://blogs.gentoo.org/ago/2017/03/20/libpcre-invalid-memory-read-in-_pcre32_xclass-pcre_xclass-c/
- https://security.gentoo.org/glsa/201710-25
- http://www.securityfocus.com/bid/97067
- https://access.redhat.com/errata/RHSA-2018:2486
