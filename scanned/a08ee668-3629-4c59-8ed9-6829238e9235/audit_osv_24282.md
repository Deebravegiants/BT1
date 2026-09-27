# [H] RDMA/rxe: Fix NULL-ptr-deref in rxe_qp_do_cleanup() when socket create failed

## Summary
Severity: High
Advisory: CVE-2022-50885
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2022-50885
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Fix NULL-ptr-deref in rxe_qp_do_cleanup() when socket create failed

There is a null-ptr-deref when mount.cifs over rdma:

  BUG: KASAN: null-ptr-deref in rxe_qp_do_cleanup+0x2f3/0x360 [rdma_rxe]
  Read of size 8 at addr 0000000000000018 by task mount.cifs/3046

  CPU: 2 PID: 3046 Comm: mount.cifs Not tainted 6.1.0-rc5+ #62
  Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.14.0-1.fc3
  Call Trace:
   <TASK>
   dump_stack_lvl+0x34/0x44
   kasan_report+0xad/0x130
   rxe_qp_do_cleanup+0x2f3/0x360 [rdma_rxe]
   execute_in_process_context+0x25/0x90
   __rxe_cleanup+0x101/0x1d0 [rdma_rxe]
   rxe_create_qp+0x16a/0x180 [rdma_rxe]
   create_qp.part.0+0x27d/0x340
   ib_create_qp_kernel+0x73/0x160
   rdma_create_qp+0x100/0x230
   _smbd_get_connection+0x752/0x20f0
   smbd_get_connection+0x21/0x40
   cifs_get_tcp_session+0x8ef/0xda0
   mount_get_conns+0x60/0x750
   cifs_mount+0x103/0xd00
   cifs_smb3_do_mount+0x1dd/0xcb0
   smb3_get_tree+0x1d5/0x300
   vfs_get_tree+0x41/0xf0
   path_mount+0x9b3/0xdd0
   __x64_sys_mount+0x190/0x1d0
   do_syscall_64+0x35/0x80
   entry_SYSCALL_64_after_hwframe+0x46/0xb0

The root cause of the issue is the socket create failed in
rxe_qp_init_req().

So move the reset rxe_qp_do_cleanup() after the NULL ptr check.

## References
- https://git.kernel.org/stable/c/5b924632d84a60bc0c7fe6e9bbbce99d03908957
- https://git.kernel.org/stable/c/6bb5a62bfd624039b05157745c234068508393a9
- https://git.kernel.org/stable/c/7340ca9f782be6fbe3f64a134dc112772764f766
- https://git.kernel.org/stable/c/821f9a18210f6b9fd6792471714c799607b25db4
- https://git.kernel.org/stable/c/bd7106a6004f1077a365ca7f5a99c7a708e20714
- https://git.kernel.org/stable/c/ee24de095569935eba600f7735e8e8ddea5b418e
- https://git.kernel.org/stable/c/f64f08b9e6fb305a25dd75329e06ae342b9ce336
- https://git.kernel.org/stable/c/f67376d801499f4fa0838c18c1efcad8840e550d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50885.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50885
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
