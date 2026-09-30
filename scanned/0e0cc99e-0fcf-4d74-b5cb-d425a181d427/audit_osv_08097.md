# [M] CVE-2016-10246

## Summary
Severity: Medium
Advisory: CVE-2016-10246
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-16
Source: https://osv.dev/vulnerability/CVE-2016-10246
Type: osv

## Details
Buffer overflow in the main function in jstest_main.c in Mujstest in Artifex Software, Inc. MuPDF before 1.10 allows remote attackers to cause a denial of service (out-of-bounds write) via a crafted file.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Bh=cfe8f35bca61056363368c343be36812abde0a06
- https://bugs.ghostscript.com/show_bug.cgi?id=697020
- http://www.openwall.com/lists/oss-security/2017/03/13/21
- https://lists.debian.org/debian-lts-announce/2021/09/msg00013.html
- https://blogs.gentoo.org/ago/2016/09/24/mupdf-mujstest-global-buffer-overflow-in-main-jstest_main-c/
