# [H] md/md-bitmap: Synchronize bitmap_get_stats() with bitmap lifetime

## Summary
Severity: High
Advisory: CVE-2025-21712
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21712
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.13 <5.15.209, >=5.16.0 <6.1.130, >=6.2.0 <6.6.80, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

md/md-bitmap: Synchronize bitmap_get_stats() with bitmap lifetime

After commit ec6bb299c7c3 ("md/md-bitmap: add 'sync_size' into struct
md_bitmap_stats"), following panic is reported:

Oops: general protection fault, probably for non-canonical address
RIP: 0010:bitmap_get_stats+0x2b/0xa0
Call Trace:
 <TASK>
 md_seq_show+0x2d2/0x5b0
 seq_read_iter+0x2b9/0x470
 seq_read+0x12f/0x180
 proc_reg_read+0x57/0xb0
 vfs_read+0xf6/0x380
 ksys_read+0x6c/0xf0
 do_syscall_64+0x82/0x170
 entry_SYSCALL_64_after_hwframe+0x76/0x7e

Root cause is that bitmap_get_stats() can be called at anytime if mddev
is still there, even if bitmap is destroyed, or not fully initialized.
Deferenceing bitmap in this case can crash the kernel. Meanwhile, the
above commit start to deferencing bitmap->storage, make the problem
easier to trigger.

Fix the problem by protecting bitmap_get_stats() with bitmap_info.mutex.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/032fa54f486eac5507976e7e31f079a767bc13a8
- https://git.kernel.org/stable/c/237e19519c8ff6949f0ef57c4a0243f5b2b0fa18
- https://git.kernel.org/stable/c/4e9316eee3885bfb311b4759513f2ccf37891c09
- https://git.kernel.org/stable/c/52848a095b55a302af92f52ca0de5b3112059bb8
- https://git.kernel.org/stable/c/8d28d0ddb986f56920ac97ae704cc3340a699a30
- https://git.kernel.org/stable/c/eb2f9d98cd3e94a79fbf8fb90637c5b12e805428
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21712.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21712
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
