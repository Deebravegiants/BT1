# [M] sysv: don't call sb_bread() with pointers_lock held

## Summary
Severity: Medium
Advisory: CVE-2023-52699
Ecosystem: Linux
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2023-52699
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.155, >=5.16.0 <6.1.86, >=6.2.0 <6.6.27, >=6.7.0 <6.8.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

sysv: don't call sb_bread() with pointers_lock held

syzbot is reporting sleep in atomic context in SysV filesystem [1], for
sb_bread() is called with rw_spinlock held.

A "write_lock(&pointers_lock) => read_lock(&pointers_lock) deadlock" bug
and a "sb_bread() with write_lock(&pointers_lock)" bug were introduced by
"Replace BKL for chain locking with sysvfs-private rwlock" in Linux 2.5.12.

Then, "[PATCH] err1-40: sysvfs locking fix" in Linux 2.6.8 fixed the
former bug by moving pointers_lock lock to the callers, but instead
introduced a "sb_bread() with read_lock(&pointers_lock)" bug (which made
this problem easier to hit).

Al Viro suggested that why not to do like get_branch()/get_block()/
find_shared() in Minix filesystem does. And doing like that is almost a
revert of "[PATCH] err1-40: sysvfs locking fix" except that get_branch()
 from with find_shared() is called without write_lock(&pointers_lock).

## References
- https://git.kernel.org/stable/c/13b33feb2ebddc2b1aa607f553566b18a4af1d76
- https://git.kernel.org/stable/c/1b4fe801b5bedec2b622ddb18e5c9bf26c63d79f
- https://git.kernel.org/stable/c/53cb1e52c9db618c08335984d1ca80db220ccf09
- https://git.kernel.org/stable/c/674c1c4229e743070e09db63a23442950ff000d1
- https://git.kernel.org/stable/c/89e8524135a3902e7563a5a59b7b5ec1bf4904ac
- https://git.kernel.org/stable/c/a69224223746ab96d43e5db9d22d136827b7e2d3
- https://git.kernel.org/stable/c/f123dc86388cb669c3d6322702dc441abc35c31e
- https://git.kernel.org/stable/c/fd203d2c671bdee9ab77090ff394d3b71b627927
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52699.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52699
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
