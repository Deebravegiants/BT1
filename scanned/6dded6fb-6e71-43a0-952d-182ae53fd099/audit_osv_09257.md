# [M] CVE-2016-9265

## Summary
Severity: Medium
Advisory: CVE-2016-9265
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-9265
Type: osv

## Details
The printMP3Headers function in listmp3.c in Libming 0.4.7 allows remote attackers to cause a denial of service (divide-by-zero error and application crash) via a crafted mp3 file.

## References
- http://www.openwall.com/lists/oss-security/2016/11/10/10
- http://www.securityfocus.com/bid/94252
- https://blogs.gentoo.org/ago/2016/11/09/libming-listmp3-divide-by-zero-in-printmp3headers-list
