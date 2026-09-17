# [M] CVE-2017-18216

## Summary
Severity: Medium
Advisory: CVE-2017-18216
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-05
Source: https://osv.dev/vulnerability/CVE-2017-18216
Type: osv

## Details
In fs/ocfs2/cluster/nodemanager.c in the Linux kernel before 4.15, local users can cause a denial of service (NULL pointer dereference and BUG) because a required mutex is not used.

## References
- https://usn.ubuntu.com/3776-2/
- https://usn.ubuntu.com/3798-1/
- https://lists.debian.org/debian-lts-announce/2018/05/msg00000.html
- https://usn.ubuntu.com/3776-1/
- https://usn.ubuntu.com/3798-2/
- https://www.debian.org/security/2018/dsa-4188
- https://www.debian.org/security/2018/dsa-4187
- http://www.securityfocus.com/bid/103278
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=853bc26a7ea39e354b9f8889ae7ad1492ffa28d2
- https://github.com/torvalds/linux/commit/853bc26a7ea39e354b9f8889ae7ad1492ffa28d2
