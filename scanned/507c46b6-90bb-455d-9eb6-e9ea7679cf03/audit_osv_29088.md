# [H] bonding: Fix out-of-bounds read in bond_option_arp_ip_targets_set()

## Summary
Severity: High
Advisory: CVE-2024-39487
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-07-09
Source: https://osv.dev/vulnerability/CVE-2024-39487
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <4.19.318, >=4.20.0 <5.4.280, >=5.5.0 <5.10.222, >=5.11.0 <5.15.163, >=5.16.0 <6.1.98, >=6.2.0 <6.6.39, >=6.7.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

bonding: Fix out-of-bounds read in bond_option_arp_ip_targets_set()

In function bond_option_arp_ip_targets_set(), if newval->string is an
empty string, newval->string+1 will point to the byte after the
string, causing an out-of-bound read.

BUG: KASAN: slab-out-of-bounds in strlen+0x7d/0xa0 lib/string.c:418
Read of size 1 at addr ffff8881119c4781 by task syz-executor665/8107
CPU: 1 PID: 8107 Comm: syz-executor665 Not tainted 6.7.0-rc7 #1
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.15.0-1 04/01/2014
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:88 [inline]
 dump_stack_lvl+0xd9/0x150 lib/dump_stack.c:106
 print_address_description mm/kasan/report.c:364 [inline]
 print_report+0xc1/0x5e0 mm/kasan/report.c:475
 kasan_report+0xbe/0xf0 mm/kasan/report.c:588
 strlen+0x7d/0xa0 lib/string.c:418
 __fortify_strlen include/linux/fortify-string.h:210 [inline]
 in4_pton+0xa3/0x3f0 net/core/utils.c:130
 bond_option_arp_ip_targets_set+0xc2/0x910
drivers/net/bonding/bond_options.c:1201
 __bond_opt_set+0x2a4/0x1030 drivers/net/bonding/bond_options.c:767
 __bond_opt_set_notify+0x48/0x150 drivers/net/bonding/bond_options.c:792
 bond_opt_tryset_rtnl+0xda/0x160 drivers/net/bonding/bond_options.c:817
 bonding_sysfs_store_option+0xa1/0x120 drivers/net/bonding/bond_sysfs.c:156
 dev_attr_store+0x54/0x80 drivers/base/core.c:2366
 sysfs_kf_write+0x114/0x170 fs/sysfs/file.c:136
 kernfs_fop_write_iter+0x337/0x500 fs/kernfs/file.c:334
 call_write_iter include/linux/fs.h:2020 [inline]
 new_sync_write fs/read_write.c:491 [inline]
 vfs_write+0x96a/0xd80 fs/read_write.c:584
 ksys_write+0x122/0x250 fs/read_write.c:637
 do_syscall_x64 arch/x86/entry/common.c:52 [inline]
 do_syscall_64+0x40/0x110 arch/x86/entry/common.c:83
 entry_SYSCALL_64_after_hwframe+0x63/0x6b
---[ end trace ]---

Fix it by adding a check of string length before using it.

## References
- https://git.kernel.org/stable/c/6a8a4fd082c439e19fede027e80c79bc4c84bb8e
- https://git.kernel.org/stable/c/6b21346b399fd1336fe59233a17eb5ce73041ee1
- https://git.kernel.org/stable/c/707c85ba3527ad6aa25552033576b0f1ff835d7b
- https://git.kernel.org/stable/c/9f835e48bd4c75fdf6a9cff3f0b806a7abde78da
- https://git.kernel.org/stable/c/b75e33eae8667084bd4a63e67657c6a5a0f8d1e8
- https://git.kernel.org/stable/c/bfd14e5915c2669f292a31d028e75dcd82f1e7e9
- https://git.kernel.org/stable/c/c8eb8ab9a44ff0e73492d0a12a643c449f641a9f
- https://git.kernel.org/stable/c/e271ff53807e8f2c628758290f0e499dbe51cb3d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39487.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39487
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
