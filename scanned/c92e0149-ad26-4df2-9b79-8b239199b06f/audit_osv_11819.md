# [H] CVE-2017-9935

## Summary
Severity: High
Advisory: CVE-2017-9935
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-06-26
Source: https://osv.dev/vulnerability/CVE-2017-9935
Type: osv

## Details
In LibTIFF 4.0.8, there is a heap-based buffer overflow in the t2p_write_pdf function in tools/tiff2pdf.c. This heap overflow could lead to different damages. For example, a crafted TIFF document can lead to an out-of-bounds read in TIFFCleanup, an invalid free in TIFFClose or t2p_free, memory corruption in t2p_readwrite_pdf_image, or a double free in t2p_free. Given these possibilities, it probably could cause arbitrary code execution.

## References
- http://www.securityfocus.com/bid/99296
- https://lists.debian.org/debian-lts-announce/2017/12/msg00008.html
- https://usn.ubuntu.com/3606-1/
- https://www.debian.org/security/2018/dsa-4100
- http://bugzilla.maptools.org/show_bug.cgi?id=2704
