# [C] CVE-2018-14352

## Summary
Severity: Critical
Advisory: CVE-2018-14352
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-17
Source: https://osv.dev/vulnerability/CVE-2018-14352
Type: osv

## Details
An issue was discovered in Mutt before 1.10.1 and NeoMutt before 2018-07-16. imap_quote_string in imap/util.c does not leave room for quote characters, leading to a stack-based buffer overflow.

## References
- http://www.mutt.org/news.html
- https://lists.debian.org/debian-lts-announce/2018/08/msg00001.html
- https://neomutt.org/2018/07/16/release
- https://security.gentoo.org/glsa/201810-07
- https://usn.ubuntu.com/3719-1/
- https://usn.ubuntu.com/3719-2/
- https://usn.ubuntu.com/3719-3/
- https://www.debian.org/security/2018/dsa-4277
- https://github.com/neomutt/neomutt/commit/e27b65b3bf8defa34db58919496056caf3850cd4
- https://gitlab.com/muttmua/mutt/commit/e0131852c6059107939893016c8ff56b6e42865d
