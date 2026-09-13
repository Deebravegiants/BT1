# [M] CVE-2017-18204

## Summary
Severity: Medium
Advisory: CVE-2017-18204
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-27
Source: https://osv.dev/vulnerability/CVE-2017-18204
Type: osv

## Details
The ocfs2_setattr function in fs/ocfs2/file.c in the Linux kernel before 4.14.2 allows local users to cause a denial of service (deadlock) via DIO requests.

## References
- https://usn.ubuntu.com/3617-1/
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3655-2/
- https://usn.ubuntu.com/3617-2/
- https://usn.ubuntu.com/3617-3/
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3655-1/
- http://www.securityfocus.com/bid/103183
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.2
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=28f5a8a7c033cbf3e32277f4cc9c6afd74f05300
- https://github.com/torvalds/linux/commit/28f5a8a7c033cbf3e32277f4cc9c6afd74f05300
