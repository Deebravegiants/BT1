# [H] CVE-2018-16509

## Summary
Severity: High
Advisory: CVE-2018-16509
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-05
Source: https://osv.dev/vulnerability/CVE-2018-16509
Type: osv

## Details
An issue was discovered in Artifex Ghostscript before 9.24. Incorrect "restoration of privilege" checking during handling of /invalidaccess exceptions could be used by attackers able to supply crafted PostScript to execute code using the "pipe" instruction.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=5516c614dc33662a2afdc377159f70218e67bde5
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=78911a01b67d590b4a91afac2e8417360b934156
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=79cccf641486a6595c43f1de1cd7ade696020a31
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=520bb0ea7519aa3e79db78aaf0589dae02103764
- https://lists.debian.org/debian-lts-announce/2018/09/msg00015.html
- https://access.redhat.com/errata/RHSA-2018:2918
- https://security.gentoo.org/glsa/201811-12
- http://www.securityfocus.com/bid/105122
- https://usn.ubuntu.com/3768-1/
- https://www.debian.org/security/2018/dsa-4294
- https://www.artifex.com/news/ghostscript-security-resolved/
- https://access.redhat.com/errata/RHSA-2018:3760
- https://bugs.ghostscript.com/show_bug.cgi?id=699654
- https://www.exploit-db.com/exploits/45369/
- http://seclists.org/oss-sec/2018/q3/142
