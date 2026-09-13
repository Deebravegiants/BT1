# [H] CVE-2017-9612

## Summary
Severity: High
Advisory: CVE-2017-9612
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-9612
Type: osv

## Details
The Ins_IP function in base/ttinterp.c in Artifex Ghostscript GhostXPS 9.21 allows remote attackers to cause a denial of service (use-after-free and application crash) or possibly have unspecified other impact via a crafted document.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=98f6da60b9d463c617e631fc254cf6d66f2e8e3c
- http://www.debian.org/security/2017/dsa-3986
- http://www.securityfocus.com/bid/99979
- https://security.gentoo.org/glsa/201811-12
- https://bugs.ghostscript.com/show_bug.cgi?id=698026
