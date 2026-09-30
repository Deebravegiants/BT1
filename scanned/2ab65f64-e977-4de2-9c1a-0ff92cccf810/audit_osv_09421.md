# [M] CVE-2016-9827

## Summary
Severity: Medium
Advisory: CVE-2016-9827
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-17
Source: https://osv.dev/vulnerability/CVE-2016-9827
Type: osv

## Details
The _iprintf function in outputtxt.c in the listswf tool in libming 0.4.7 allows remote attackers to cause a denial of service (buffer over-read) via a crafted SWF file.

## References
- http://www.securityfocus.com/bid/95086
- http://www.openwall.com/lists/oss-security/2016/12/05/2
- http://www.openwall.com/lists/oss-security/2016/12/01/7
- https://blogs.gentoo.org/ago/2016/12/01/libming-listswf-heap-based-buffer-overflow-in-_iprintf-outputtxt-c/
