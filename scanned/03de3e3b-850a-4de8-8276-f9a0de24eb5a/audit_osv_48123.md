# [H] CVE-2017-18249

## Summary
Severity: High
Advisory: CVE-2017-18249
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-26
Source: https://osv.dev/vulnerability/CVE-2017-18249
Type: osv

## Details
The add_free_nid function in fs/f2fs/node.c in the Linux kernel before 4.12 does not properly track an allocated nid, which allows local users to cause a denial of service (race condition) or possibly have unspecified other impact via concurrent threads.

## References
- https://usn.ubuntu.com/3932-1/
- https://usn.ubuntu.com/3932-2/
- https://lists.debian.org/debian-lts-announce/2019/03/msg00017.html
- http://www.securitytracker.com/id/1041432
- https://github.com/torvalds/linux/commit/30a61ddf8117c26ac5b295e1233eaa9629a94ca3
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=30a61ddf8117c26ac5b295e1233eaa9629a94ca3
