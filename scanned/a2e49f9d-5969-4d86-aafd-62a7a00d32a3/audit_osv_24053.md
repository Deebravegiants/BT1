# [H] SUNRPC: Fix null-ptr-deref when xps sysfs alloc failed

## Summary
Severity: High
Advisory: CVE-2022-49928
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49928
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

SUNRPC: Fix null-ptr-deref when xps sysfs alloc failed

There is a null-ptr-deref when xps sysfs alloc failed:
  BUG: KASAN: null-ptr-deref in sysfs_do_create_link_sd+0x40/0xd0
  Read of size 8 at addr 0000000000000030 by task gssproxy/457

  CPU: 5 PID: 457 Comm: gssproxy Not tainted 6.0.0-09040-g02357b27ee03 #9
  Call Trace:
   <TASK>
   dump_stack_lvl+0x34/0x44
   kasan_report+0xa3/0x120
   sysfs_do_create_link_sd+0x40/0xd0
   rpc_sysfs_client_setup+0x161/0x1b0
   rpc_new_client+0x3fc/0x6e0
   rpc_create_xprt+0x71/0x220
   rpc_create+0x1d4/0x350
   gssp_rpc_create+0xc3/0x160
   set_gssp_clnt+0xbc/0x140
   write_gssp+0x116/0x1a0
   proc_reg_write+0xd6/0x130
   vfs_write+0x177/0x690
   ksys_write+0xb9/0x150
   do_syscall_64+0x35/0x80
   entry_SYSCALL_64_after_hwframe+0x46/0xb0

When the xprt_switch sysfs alloc failed, should not add xprt and
switch sysfs to it, otherwise, maybe null-ptr-deref; also initialize
the 'xps_sysfs' to NULL to avoid oops when destroy it.

## References
- https://git.kernel.org/stable/c/7b189b0aa8dab14b49c31c65af8a982e96e25b62
- https://git.kernel.org/stable/c/cbdeaee94a415800c65a8c3fa04d9664a8b8fb3a
- https://git.kernel.org/stable/c/d59722d088a9d86ce6d9d39979e5d1d669d249f7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49928.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49928
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
