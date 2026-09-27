# [M] CVE-2016-9264

## Summary
Severity: Medium
Advisory: CVE-2016-9264
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-9264
Type: osv

## Details
Buffer overflow in the printMP3Headers function in listmp3.c in Libming 0.4.7 allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted mp3 file.

## References
- http://www.openwall.com/lists/oss-security/2016/11/10/9
- http://www.securityfocus.com/bid/94251
- https://blogs.gentoo.org/ago/2016/11/07/libming-listmp3-global-buffer-overflow-in-printmp3headers-listmp3-c/
