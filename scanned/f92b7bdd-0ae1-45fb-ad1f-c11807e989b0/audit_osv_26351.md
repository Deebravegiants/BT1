# [H] can: bcm: Fix UAF in bcm_proc_show()

## Summary
Severity: High
Advisory: CVE-2023-52922
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-28
Source: https://osv.dev/vulnerability/CVE-2023-52922
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <4.14.322, >=4.15.0 <4.19.291, >=4.20.0 <5.4.251, >=5.5.0 <5.10.188, >=5.11.0 <5.15.123, >=5.16.0 <6.1.42, >=6.2.0 <6.4.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: bcm: Fix UAF in bcm_proc_show()

BUG: KASAN: slab-use-after-free in bcm_proc_show+0x969/0xa80
Read of size 8 at addr ffff888155846230 by task cat/7862

CPU: 1 PID: 7862 Comm: cat Not tainted 6.5.0-rc1-00153-gc8746099c197 #230
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.15.0-1 04/01/2014
Call Trace:
 <TASK>
 dump_stack_lvl+0xd5/0x150
 print_report+0xc1/0x5e0
 kasan_report+0xba/0xf0
 bcm_proc_show+0x969/0xa80
 seq_read_iter+0x4f6/0x1260
 seq_read+0x165/0x210
 proc_reg_read+0x227/0x300
 vfs_read+0x1d5/0x8d0
 ksys_read+0x11e/0x240
 do_syscall_64+0x35/0xb0
 entry_SYSCALL_64_after_hwframe+0x63/0xcd

Allocated by task 7846:
 kasan_save_stack+0x1e/0x40
 kasan_set_track+0x21/0x30
 __kasan_kmalloc+0x9e/0xa0
 bcm_sendmsg+0x264b/0x44e0
 sock_sendmsg+0xda/0x180
 ____sys_sendmsg+0x735/0x920
 ___sys_sendmsg+0x11d/0x1b0
 __sys_sendmsg+0xfa/0x1d0
 do_syscall_64+0x35/0xb0
 entry_SYSCALL_64_after_hwframe+0x63/0xcd

Freed by task 7846:
 kasan_save_stack+0x1e/0x40
 kasan_set_track+0x21/0x30
 kasan_save_free_info+0x27/0x40
 ____kasan_slab_free+0x161/0x1c0
 slab_free_freelist_hook+0x119/0x220
 __kmem_cache_free+0xb4/0x2e0
 rcu_core+0x809/0x1bd0

bcm_op is freed before procfs entry be removed in bcm_release(),
this lead to bcm_proc_show() may read the freed bcm_op.

## References
- https://allelesecurity.com/use-after-free-vulnerability-in-can-bcm-subsystem-leading-to-information-disclosure-cve-2023-52922/
- https://git.kernel.org/stable/c/11b8e27ed448baa385d90154a141466bd5e92f18
- https://git.kernel.org/stable/c/3c3941bb1eb53abe7d640ffee5c4d6b559829ab3
- https://git.kernel.org/stable/c/55c3b96074f3f9b0aee19bf93cd71af7516582bb
- https://git.kernel.org/stable/c/9533dbfac0ff7edd77a5fa2c24974b1d66c8b0a6
- https://git.kernel.org/stable/c/995f47d76647708ec26c6e388663ad4f3f264787
- https://git.kernel.org/stable/c/9b58d36d0c1ea29a9571e0222a9c29df0ccfb7ff
- https://git.kernel.org/stable/c/cf254b4f68e480e73dab055014e002b77aed30ed
- https://git.kernel.org/stable/c/dfd0aa26e9a07f2ce546ccf8304ead6a2914e8a7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52922.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52922
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
