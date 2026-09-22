# [H] erofs: fix pcluster use-after-free on UP platforms

## Summary
Severity: High
Advisory: CVE-2022-48674
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2022-48674
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.15.68, >=5.16.0 <5.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

erofs: fix pcluster use-after-free on UP platforms

During stress testing with CONFIG_SMP disabled, KASAN reports as below:

==================================================================
BUG: KASAN: use-after-free in __mutex_lock+0xe5/0xc30
Read of size 8 at addr ffff8881094223f8 by task stress/7789

CPU: 0 PID: 7789 Comm: stress Not tainted 6.0.0-rc1-00002-g0d53d2e882f9 #3
Hardware name: Red Hat KVM, BIOS 0.5.1 01/01/2011
Call Trace:
 <TASK>
..
 __mutex_lock+0xe5/0xc30
..
 z_erofs_do_read_page+0x8ce/0x1560
..
 z_erofs_readahead+0x31c/0x580
..
Freed by task 7787
 kasan_save_stack+0x1e/0x40
 kasan_set_track+0x20/0x30
 kasan_set_free_info+0x20/0x40
 __kasan_slab_free+0x10c/0x190
 kmem_cache_free+0xed/0x380
 rcu_core+0x3d5/0xc90
 __do_softirq+0x12d/0x389

Last potentially related work creation:
 kasan_save_stack+0x1e/0x40
 __kasan_record_aux_stack+0x97/0xb0
 call_rcu+0x3d/0x3f0
 erofs_shrink_workstation+0x11f/0x210
 erofs_shrink_scan+0xdc/0x170
 shrink_slab.constprop.0+0x296/0x530
 drop_slab+0x1c/0x70
 drop_caches_sysctl_handler+0x70/0x80
 proc_sys_call_handler+0x20a/0x2f0
 vfs_write+0x555/0x6c0
 ksys_write+0xbe/0x160
 do_syscall_64+0x3b/0x90

The root cause is that erofs_workgroup_unfreeze() doesn't reset to
orig_val thus it causes a race that the pcluster reuses unexpectedly
before freeing.

Since UP platforms are quite rare now, such path becomes unnecessary.
Let's drop such specific-designed path directly instead.

## References
- https://git.kernel.org/stable/c/2f44013e39984c127c6efedf70e6b5f4e9dcf315
- https://git.kernel.org/stable/c/8ddd001cef5e82d19192e6861068463ecca5f556
- https://git.kernel.org/stable/c/94c34faaafe7b55adc2d8d881db195b646959b9e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48674.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48674
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
