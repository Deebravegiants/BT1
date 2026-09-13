# [M] CVE-2015-9101

## Summary
Severity: Medium
Advisory: CVE-2015-9101
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-25
Source: https://osv.dev/vulnerability/CVE-2015-9101
Type: osv

## Details
The fill_buffer_resample function in util.c in libmp3lame.a in LAME 3.98.4, 3.98.2, 3.98, 3.99, 3.99.1, 3.99.2, 3.99.3, 3.99.4 and 3.99.5 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted audio file.

## References
- http://www.securityfocus.com/bid/99269
- https://blogs.gentoo.org/ago/2017/06/17/lame-heap-based-buffer-overflow-in-fill_buffer_resample-util-c/
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=777161
- https://github.com/Hack-Me/Pocs_for_Multi_Versions/tree/main/CVE-2015-9101
- https://github.com/Hack-Me/Pocs_for_Multi_Versions/tree/main/CVE-2015-9101
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=777161
