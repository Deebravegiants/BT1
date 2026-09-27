# [M] CVE-2016-10247

## Summary
Severity: Medium
Advisory: CVE-2016-10247
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-16
Source: https://osv.dev/vulnerability/CVE-2016-10247
Type: osv

## Details
Buffer overflow in the my_getline function in jstest_main.c in Mujstest in Artifex Software, Inc. MuPDF before 1.10 allows remote attackers to cause a denial of service (out-of-bounds write) via a crafted file.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Bh=446097f97b71ce20fa8d1e45e070f2e62676003e
- https://bugs.ghostscript.com/show_bug.cgi?id=697021
- http://www.openwall.com/lists/oss-security/2017/03/13/20
- http://www.securityfocus.com/bid/97099
- https://lists.debian.org/debian-lts-announce/2021/09/msg00013.html
- https://blogs.gentoo.org/ago/2016/09/24/mupdf-mujstest-global-buffer-overflow-in-my_getline-jstest_main-c/
