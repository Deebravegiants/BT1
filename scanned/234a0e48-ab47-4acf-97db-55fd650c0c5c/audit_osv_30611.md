# [H] scsi: bfa: Fix use-after-free in bfad_im_module_exit()

## Summary
Severity: High
Advisory: CVE-2024-53227
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53227
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.32 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: bfa: Fix use-after-free in bfad_im_module_exit()

BUG: KASAN: slab-use-after-free in __lock_acquire+0x2aca/0x3a20
Read of size 8 at addr ffff8881082d80c8 by task modprobe/25303

Call Trace:
 <TASK>
 dump_stack_lvl+0x95/0xe0
 print_report+0xcb/0x620
 kasan_report+0xbd/0xf0
 __lock_acquire+0x2aca/0x3a20
 lock_acquire+0x19b/0x520
 _raw_spin_lock+0x2b/0x40
 attribute_container_unregister+0x30/0x160
 fc_release_transport+0x19/0x90 [scsi_transport_fc]
 bfad_im_module_exit+0x23/0x60 [bfa]
 bfad_init+0xdb/0xff0 [bfa]
 do_one_initcall+0xdc/0x550
 do_init_module+0x22d/0x6b0
 load_module+0x4e96/0x5ff0
 init_module_from_file+0xcd/0x130
 idempotent_init_module+0x330/0x620
 __x64_sys_finit_module+0xb3/0x110
 do_syscall_64+0xc1/0x1d0
 entry_SYSCALL_64_after_hwframe+0x77/0x7f
 </TASK>

Allocated by task 25303:
 kasan_save_stack+0x24/0x50
 kasan_save_track+0x14/0x30
 __kasan_kmalloc+0x7f/0x90
 fc_attach_transport+0x4f/0x4740 [scsi_transport_fc]
 bfad_im_module_init+0x17/0x80 [bfa]
 bfad_init+0x23/0xff0 [bfa]
 do_one_initcall+0xdc/0x550
 do_init_module+0x22d/0x6b0
 load_module+0x4e96/0x5ff0
 init_module_from_file+0xcd/0x130
 idempotent_init_module+0x330/0x620
 __x64_sys_finit_module+0xb3/0x110
 do_syscall_64+0xc1/0x1d0
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

Freed by task 25303:
 kasan_save_stack+0x24/0x50
 kasan_save_track+0x14/0x30
 kasan_save_free_info+0x3b/0x60
 __kasan_slab_free+0x38/0x50
 kfree+0x212/0x480
 bfad_im_module_init+0x7e/0x80 [bfa]
 bfad_init+0x23/0xff0 [bfa]
 do_one_initcall+0xdc/0x550
 do_init_module+0x22d/0x6b0
 load_module+0x4e96/0x5ff0
 init_module_from_file+0xcd/0x130
 idempotent_init_module+0x330/0x620
 __x64_sys_finit_module+0xb3/0x110
 do_syscall_64+0xc1/0x1d0
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

Above issue happens as follows:

bfad_init
  error = bfad_im_module_init()
    fc_release_transport(bfad_im_scsi_transport_template);
  if (error)
    goto ext;

ext:
  bfad_im_module_exit();
    fc_release_transport(bfad_im_scsi_transport_template);
    --> Trigger double release

Don't call bfad_im_module_exit() if bfad_im_module_init() failed.

## References
- https://git.kernel.org/stable/c/0ceac8012d3ddea3317f0d82934293d05feb8af1
- https://git.kernel.org/stable/c/178b8f38932d635e90f5f0e9af1986c6f4a89271
- https://git.kernel.org/stable/c/1ffdde30a90bf8efe8f270407f486706962b3292
- https://git.kernel.org/stable/c/3932c753f805a02e9364a4c58b590f21901f8490
- https://git.kernel.org/stable/c/8f5a97443b547b4c83f876f1d6a11df0f1fd4efb
- https://git.kernel.org/stable/c/a2b5035ab0e368e8d8a371e27fbc72f133c0bd40
- https://git.kernel.org/stable/c/c28409f851abd93b37969cac7498828ad533afd9
- https://git.kernel.org/stable/c/e76181a5be90abcc3ed8a300bd13878aa214d022
- https://git.kernel.org/stable/c/ef2c2580189ea88a0dcaf56eb3a565763a900edb
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53227.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53227
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
