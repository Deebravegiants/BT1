# [M] ext4: fix mb_cache_entry's e_refcnt leak in ext4_xattr_block_cache_find()

## Summary
Severity: Medium
Advisory: CVE-2024-39276
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-06-25
Source: https://osv.dev/vulnerability/CVE-2024-39276
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.316, >=4.20.0 <5.4.278, >=5.0.0 <5.10.219, >=5.5.0 <5.15.161, >=5.11.0 <6.1.94, >=5.16.0 <6.6.34, >=6.2.0 <6.9.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix mb_cache_entry's e_refcnt leak in ext4_xattr_block_cache_find()

Syzbot reports a warning as follows:

============================================
WARNING: CPU: 0 PID: 5075 at fs/mbcache.c:419 mb_cache_destroy+0x224/0x290
Modules linked in:
CPU: 0 PID: 5075 Comm: syz-executor199 Not tainted 6.9.0-rc6-gb947cc5bf6d7
RIP: 0010:mb_cache_destroy+0x224/0x290 fs/mbcache.c:419
Call Trace:
 <TASK>
 ext4_put_super+0x6d4/0xcd0 fs/ext4/super.c:1375
 generic_shutdown_super+0x136/0x2d0 fs/super.c:641
 kill_block_super+0x44/0x90 fs/super.c:1675
 ext4_kill_sb+0x68/0xa0 fs/ext4/super.c:7327
[...]
============================================

This is because when finding an entry in ext4_xattr_block_cache_find(), if
ext4_sb_bread() returns -ENOMEM, the ce's e_refcnt, which has already grown
in the __entry_find(), won't be put away, and eventually trigger the above
issue in mb_cache_destroy() due to reference count leakage.

So call mb_cache_entry_put() on the -ENOMEM error branch as a quick fix.

## References
- https://git.kernel.org/stable/c/0c0b4a49d3e7f49690a6827a41faeffad5df7e21
- https://git.kernel.org/stable/c/681ff9a09accd8a4379f8bd30b7a1641ee19bb3e
- https://git.kernel.org/stable/c/76dc776153a47372719d664e0fc50d6355791abb
- https://git.kernel.org/stable/c/896a7e7d0d555ad8b2b46af0c2fa7de7467f9483
- https://git.kernel.org/stable/c/9ad75e78747b5a50dc5a52f0f8e92e920a653f16
- https://git.kernel.org/stable/c/a95df6f04f2c37291adf26a74205cde0314d4577
- https://git.kernel.org/stable/c/b37c0edef4e66fb21a2fbc211471195a383e5ab8
- https://git.kernel.org/stable/c/e941b712e758f615d311946bf98216e79145ccd9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39276.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39276
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
