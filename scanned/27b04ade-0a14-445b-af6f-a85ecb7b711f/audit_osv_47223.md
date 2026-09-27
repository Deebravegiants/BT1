# [H] CVE-2016-1244

## Summary
Severity: High
Advisory: CVE-2016-1244
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/CVE-2016-1244
Type: osv

## Details
The extractTree function in unADF allows remote attackers to execute arbitrary code via shell metacharacters in a directory name in an adf file.

## References
- http://www.securityfocus.com/bid/93332
- https://lists.debian.org/debian-lts-announce/2024/03/msg00015.html
- https://security.gentoo.org/glsa/201804-20
- http://www.debian.org/security/2016/dsa-3676
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=838248
- http://tmp.tjjr.fi/0001-Fix-unsafe-extraction-by-using-mkdir-instead-of-shel.patch
