# [H] hfs: fix OOB Read in __hfs_brec_find

## Summary
Severity: High
Advisory: CVE-2022-50581
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/CVE-2022-50581
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

hfs: fix OOB Read in __hfs_brec_find

Syzbot reported a OOB read bug:

==================================================================
BUG: KASAN: slab-out-of-bounds in hfs_strcmp+0x117/0x190
fs/hfs/string.c:84
Read of size 1 at addr ffff88807eb62c4e by task kworker/u4:1/11
CPU: 1 PID: 11 Comm: kworker/u4:1 Not tainted
6.1.0-rc6-syzkaller-00308-g644e9524388a #0
Workqueue: writeback wb_workfn (flush-7:0)
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:88 [inline]
 dump_stack_lvl+0x1b1/0x28e lib/dump_stack.c:106
 print_address_description+0x74/0x340 mm/kasan/report.c:284
 print_report+0x107/0x1f0 mm/kasan/report.c:395
 kasan_report+0xcd/0x100 mm/kasan/report.c:495
 hfs_strcmp+0x117/0x190 fs/hfs/string.c:84
 __hfs_brec_find+0x213/0x5c0 fs/hfs/bfind.c:75
 hfs_brec_find+0x276/0x520 fs/hfs/bfind.c:138
 hfs_write_inode+0x34c/0xb40 fs/hfs/inode.c:462
 write_inode fs/fs-writeback.c:1440 [inline]

If the input inode of hfs_write_inode() is incorrect:
struct inode
  struct hfs_inode_info
    struct hfs_cat_key
      struct hfs_name
        u8 len # len is greater than HFS_NAMELEN(31) which is the
maximum length of an HFS filename

OOB read occurred:
hfs_write_inode()
  hfs_brec_find()
    __hfs_brec_find()
      hfs_cat_keycmp()
        hfs_strcmp() # OOB read occurred due to len is too large

Fix this by adding a Check on len in hfs_write_inode() before calling
hfs_brec_find().

## References
- https://git.kernel.org/stable/c/2344f17c0a89c181ab1a9fef57fd8c3bddfd6e30
- https://git.kernel.org/stable/c/367296925c7625c3969d2a78d7a3e1dee161beb5
- https://git.kernel.org/stable/c/4fd3a11804c8877ff11fec59c5c53f1635331e3e
- https://git.kernel.org/stable/c/8c40f2dbae603ef0bd21e87c63f54ec59fd88256
- https://git.kernel.org/stable/c/8d824e69d9f3fa3121b2dda25053bae71e2460d2
- https://git.kernel.org/stable/c/90103ccb6e60aa4efe48993d23d6a528472f2233
- https://git.kernel.org/stable/c/bfc9d8f27f89717431a6aecce42ae230b437433f
- https://git.kernel.org/stable/c/c886c10a6eddb99923b315f42bf63f448883ef9a
- https://git.kernel.org/stable/c/e9e692917c6e10a7066c7a6d092dcdc3d4e329f3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50581.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50581
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
