# [M] CVE-2016-8674

## Summary
Severity: Medium
Advisory: CVE-2016-8674
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2016-8674
Type: osv

## Details
The pdf_to_num function in pdf-object.c in MuPDF before 1.10 allows remote attackers to cause a denial of service (use-after-free and application crash) via a crafted file.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Ba=commitdiff%3Bh=1e03c06456d997435019fb3526fa2d4be7dbc6ec
- http://www.debian.org/security/2017/dsa-3797
- http://www.securityfocus.com/bid/93127
- http://www.openwall.com/lists/oss-security/2016/10/16/8
- https://blogs.gentoo.org/ago/2016/09/22/mupdf-use-after-free-in-pdf_to_num-pdf-object-c/
- https://bugs.ghostscript.com/show_bug.cgi?id=697015
- https://bugs.ghostscript.com/show_bug.cgi?id=697019
- https://bugzilla.redhat.com/show_bug.cgi?id=1385685
