# [C] CVE-2018-14362

## Summary
Severity: Critical
Advisory: CVE-2018-14362
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-17
Source: https://osv.dev/vulnerability/CVE-2018-14362
Type: osv

## Details
An issue was discovered in Mutt before 1.10.1 and NeoMutt before 2018-07-16. pop.c does not forbid characters that may have unsafe interaction with message-cache pathnames, as demonstrated by a '/' character.

## References
- http://www.mutt.org/news.html
- https://access.redhat.com/errata/RHSA-2018:2526
- https://lists.debian.org/debian-lts-announce/2018/08/msg00001.html
- https://neomutt.org/2018/07/16/release
- https://security.gentoo.org/glsa/201810-07
- https://usn.ubuntu.com/3719-3/
- https://www.debian.org/security/2018/dsa-4277
- https://github.com/neomutt/neomutt/commit/9bfab35522301794483f8f9ed60820bdec9be59e
- https://gitlab.com/muttmua/mutt/commit/6aed28b40a0410ec47d40c8c7296d8d10bae7576
