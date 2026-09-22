# [M] CVE-2018-1000036

## Summary
Severity: Medium
Advisory: CVE-2018-1000036
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-24
Source: https://osv.dev/vulnerability/CVE-2018-1000036
Type: osv

## Details
In Artifex MuPDF 1.12.0 and earlier, multiple memory leaks in the PDF parser allow an attacker to cause a denial of service (memory leak) via a crafted file.

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=698887
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/commit/?id=8aa2bd34065d2844aae778bd4cc20c74bbcd9406
- https://lists.debian.org/debian-lts-announce/2021/09/msg00013.html
- https://security.gentoo.org/glsa/201811-15
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=5502
