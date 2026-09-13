# [H] CVE-2018-5764

## Summary
Severity: High
Advisory: CVE-2018-5764
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-01-17
Source: https://osv.dev/vulnerability/CVE-2018-5764
Type: osv

## Details
The parse_arguments function in options.c in rsyncd in rsync before 3.1.3 does not prevent multiple --protect-args uses, which allows remote attackers to bypass an argument-sanitization protection mechanism.

## References
- https://git.samba.org/rsync.git/?p=rsync.git%3Ba=commit%3Bh=7706303828fcde524222babb2833864a4bd09e07
- http://www.securityfocus.com/bid/102803
- http://www.securitytracker.com/id/1040276
- https://download.samba.org/pub/rsync/src-previews/rsync-3.1.3pre1-NEWS
- https://lists.debian.org/debian-lts-announce/2018/01/msg00021.html
- https://lists.debian.org/debian-lts-announce/2019/03/msg00027.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00028.html
- https://security.gentoo.org/glsa/201805-04
- https://usn.ubuntu.com/3543-1/
