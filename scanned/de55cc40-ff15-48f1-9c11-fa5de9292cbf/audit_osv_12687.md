# [M] CVE-2018-14355

## Summary
Severity: Medium
Advisory: CVE-2018-14355
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-07-17
Source: https://osv.dev/vulnerability/CVE-2018-14355
Type: osv

## Details
An issue was discovered in Mutt before 1.10.1 and NeoMutt before 2018-07-16. imap/util.c mishandles ".." directory traversal in a mailbox name.

## References
- http://www.mutt.org/news.html
- https://lists.debian.org/debian-lts-announce/2018/08/msg00001.html
- https://neomutt.org/2018/07/16/release
- https://security.gentoo.org/glsa/201810-07
- https://usn.ubuntu.com/3719-3/
- https://www.debian.org/security/2018/dsa-4277
- https://github.com/neomutt/neomutt/commit/57971dba06346b2d7179294f4528b8d4427a7c5d
- https://gitlab.com/muttmua/mutt/commit/31eef6c766f47df8281942d19f76e35f475c781d
