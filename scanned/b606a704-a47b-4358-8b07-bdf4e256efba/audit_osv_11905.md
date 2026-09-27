# [H] CVE-2018-1000051

## Summary
Severity: High
Advisory: CVE-2018-1000051
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/CVE-2018-1000051
Type: osv

## Details
Artifex Mupdf version 1.12.0 contains a Use After Free vulnerability in fz_keep_key_storable that can result in DOS / Possible code execution. This attack appear to be exploitable via Victim opens a specially crafted PDF.

## References
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/commit/?id=321ba1de287016b0036bf4a56ce774ad11763384
- https://security.gentoo.org/glsa/201811-15
- https://www.debian.org/security/2018/dsa-4152
- https://bugs.ghostscript.com/show_bug.cgi?id=698873
- https://bugs.ghostscript.com/show_bug.cgi?id=698825
