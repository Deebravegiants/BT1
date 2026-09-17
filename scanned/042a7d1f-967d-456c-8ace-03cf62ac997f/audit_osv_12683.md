# [C] CVE-2018-14351

## Summary
Severity: Critical
Advisory: CVE-2018-14351
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-17
Source: https://osv.dev/vulnerability/CVE-2018-14351
Type: osv

## Details
An issue was discovered in Mutt before 1.10.1 and NeoMutt before 2018-07-16. imap/command.c mishandles a long IMAP status mailbox literal count size.

## References
- http://www.mutt.org/news.html
- https://lists.debian.org/debian-lts-announce/2018/08/msg00001.html
- https://neomutt.org/2018/07/16/release
- https://security.gentoo.org/glsa/201810-07
- https://usn.ubuntu.com/3719-3/
- https://www.debian.org/security/2018/dsa-4277
- https://github.com/neomutt/neomutt/commit/3c49c44be9b459d9c616bcaef6eb5d51298c1741
- https://gitlab.com/muttmua/mutt/commit/e57a8602b45f58edf7b3ffb61bb17525d75dfcb1
