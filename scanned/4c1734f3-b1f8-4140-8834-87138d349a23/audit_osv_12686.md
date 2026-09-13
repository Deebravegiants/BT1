# [C] CVE-2018-14354

## Summary
Severity: Critical
Advisory: CVE-2018-14354
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-17
Source: https://osv.dev/vulnerability/CVE-2018-14354
Type: osv

## Details
An issue was discovered in Mutt before 1.10.1 and NeoMutt before 2018-07-16. They allow remote IMAP servers to execute arbitrary commands via backquote characters, related to the mailboxes command associated with a manual subscription or unsubscription.

## References
- http://www.mutt.org/news.html
- http://www.securityfocus.com/bid/104925
- https://access.redhat.com/errata/RHSA-2018:2526
- https://lists.debian.org/debian-lts-announce/2018/08/msg00001.html
- https://neomutt.org/2018/07/16/release
- https://security.gentoo.org/glsa/201810-07
- https://usn.ubuntu.com/3719-1/
- https://usn.ubuntu.com/3719-2/
- https://usn.ubuntu.com/3719-3/
- https://www.debian.org/security/2018/dsa-4277
- https://github.com/neomutt/neomutt/commit/95e80bf9ff10f68cb6443f760b85df4117cb15eb
- https://gitlab.com/muttmua/mutt/commit/185152818541f5cdc059cbff3f3e8b654fc27c1d
