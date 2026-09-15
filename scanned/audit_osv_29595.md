# [H] jfs: fix null ptr deref in dtInsertEntry

## Summary
Severity: High
Advisory: CVE-2024-44939
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-26
Source: https://osv.dev/vulnerability/CVE-2024-44939
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.15.189, >=5.16.0 <6.1.107, >=6.2.0 <6.6.47, >=6.7.0 <6.10.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

jfs: fix null ptr deref in dtInsertEntry

[syzbot reported]
general protection fault, probably for non-canonical address 0xdffffc0000000001: 0000 [#1] PREEMPT SMP KASAN PTI
KASAN: null-ptr-deref in range [0x0000000000000008-0x000000000000000f]
CPU: 0 PID: 5061 Comm: syz-executor404 Not tainted 6.8.0-syzkaller-08951-gfe46a7dd189e #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 03/27/2024
RIP: 0010:dtInsertEntry+0xd0c/0x1780 fs/jfs/jfs_dtree.c:3713
...
[Analyze]
In dtInsertEntry(), when the pointer h has the same value as p, after writing
name in UniStrncpy_to_le(), p->header.flag will be cleared. This will cause the
previously true judgment "p->header.flag & BT-LEAF" to change to no after writing
the name operation, this leads to entering an incorrect branch and accessing the
uninitialized object ih when judging this condition for the second time.

[Fix]
After got the page, check freelist first, if freelist == 0 then exit dtInsert()
and return -EINVAL.

## References
- https://git.kernel.org/stable/c/53023ab11836ac56fd75f7a71ec1356e50920fa9
- https://git.kernel.org/stable/c/6ea10dbb1e6c58384136e9adfd75f81951e423f6
- https://git.kernel.org/stable/c/9c2ac38530d1a3ee558834dfa16c85a40fd0e702
- https://git.kernel.org/stable/c/ce6dede912f064a855acf6f04a04cbb2c25b8c8c
- https://git.kernel.org/stable/c/f98bf80b20f4a930589cda48a35f751a64fe0dc2
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44939.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44939
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
