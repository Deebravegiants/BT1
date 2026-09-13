# [M] CVE-2018-5759

## Summary
Severity: Medium
Advisory: CVE-2018-5759
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-24
Source: https://osv.dev/vulnerability/CVE-2018-5759
Type: osv

## Details
jsparse.c in Artifex MuJS through 1.0.2 does not properly maintain the AST depth for binary expressions, which allows remote attackers to cause a denial of service (excessive recursion) via a crafted file.

## References
- http://git.ghostscript.com/?p=mujs.git%3Ba=commit%3Bh=4d45a96e57fbabf00a7378b337d0ddcace6f38c1
- http://www.securityfocus.com/bid/102833
- https://bugs.ghostscript.com/show_bug.cgi?id=698868
- https://www.exploit-db.com/exploits/43904/
