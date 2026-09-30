# [H] dm: call the resume method on internal suspend

## Summary
Severity: High
Advisory: CVE-2024-26880
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26880
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <4.19.311, >=4.20.0 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

dm: call the resume method on internal suspend

There is this reported crash when experimenting with the lvm2 testsuite.
The list corruption is caused by the fact that the postsuspend and resume
methods were not paired correctly; there were two consecutive calls to the
origin_postsuspend function. The second call attempts to remove the
"hash_list" entry from a list, while it was already removed by the first
call.

Fix __dm_internal_resume so that it calls the preresume and resume
methods of the table's targets.

If a preresume method of some target fails, we are in a tricky situation.
We can't return an error because dm_internal_resume isn't supposed to
return errors. We can't return success, because then the "resume" and
"postsuspend" methods would not be paired correctly. So, we set the
DMF_SUSPENDED flag and we fake normal suspend - it may confuse userspace
tools, but it won't cause a kernel crash.

------------[ cut here ]------------
kernel BUG at lib/list_debug.c:56!
invalid opcode: 0000 [#1] PREEMPT SMP
CPU: 1 PID: 8343 Comm: dmsetup Not tainted 6.8.0-rc6 #4
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.14.0-2 04/01/2014
RIP: 0010:__list_del_entry_valid_or_report+0x77/0xc0
<snip>
RSP: 0018:ffff8881b831bcc0 EFLAGS: 00010282
RAX: 000000000000004e RBX: ffff888143b6eb80 RCX: 0000000000000000
RDX: 0000000000000001 RSI: ffffffff819053d0 RDI: 00000000ffffffff
RBP: ffff8881b83a3400 R08: 00000000fffeffff R09: 0000000000000058
R10: 0000000000000000 R11: ffffffff81a24080 R12: 0000000000000001
R13: ffff88814538e000 R14: ffff888143bc6dc0 R15: ffffffffa02e4bb0
FS:  00000000f7c0f780(0000) GS:ffff8893f0a40000(0000) knlGS:0000000000000000
CS:  0010 DS: 002b ES: 002b CR0: 0000000080050033
CR2: 0000000057fb5000 CR3: 0000000143474000 CR4: 00000000000006b0
Call Trace:
 <TASK>
 ? die+0x2d/0x80
 ? do_trap+0xeb/0xf0
 ? __list_del_entry_valid_or_report+0x77/0xc0
 ? do_error_trap+0x60/0x80
 ? __list_del_entry_valid_or_report+0x77/0xc0
 ? exc_invalid_op+0x49/0x60
 ? __list_del_entry_valid_or_report+0x77/0xc0
 ? asm_exc_invalid_op+0x16/0x20
 ? table_deps+0x1b0/0x1b0 [dm_mod]
 ? __list_del_entry_valid_or_report+0x77/0xc0
 origin_postsuspend+0x1a/0x50 [dm_snapshot]
 dm_table_postsuspend_targets+0x34/0x50 [dm_mod]
 dm_suspend+0xd8/0xf0 [dm_mod]
 dev_suspend+0x1f2/0x2f0 [dm_mod]
 ? table_deps+0x1b0/0x1b0 [dm_mod]
 ctl_ioctl+0x300/0x5f0 [dm_mod]
 dm_compat_ctl_ioctl+0x7/0x10 [dm_mod]
 __x64_compat_sys_ioctl+0x104/0x170
 do_syscall_64+0x184/0x1b0
 entry_SYSCALL_64_after_hwframe+0x46/0x4e
RIP: 0033:0xf7e6aead
<snip>
---[ end trace 0000000000000000 ]---

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://git.kernel.org/stable/c/03ad5ad53e51abf3a4c7538c1bc67a5982b41dc5
- https://git.kernel.org/stable/c/15a3fc5c8774c17589dabfe1d642d40685c985af
- https://git.kernel.org/stable/c/360a7d1be8112654f1fb328ed3862be630bca3f4
- https://git.kernel.org/stable/c/65e8fbde64520001abf1c8d0e573561b4746ef38
- https://git.kernel.org/stable/c/69836d9329f0b4c58faaf3d886a7748ddb5bf718
- https://git.kernel.org/stable/c/ad10289f68f45649816cc68eb93f45fd5ec48a15
- https://git.kernel.org/stable/c/da7ece2197101b1469853e6b5e915be1e3896d52
- https://git.kernel.org/stable/c/ef02d8edf738557af2865c5bfb66a03c4e071be7
- https://git.kernel.org/stable/c/f89bd27709376d37ff883067193320c58a8c1d5a
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26880.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26880
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
