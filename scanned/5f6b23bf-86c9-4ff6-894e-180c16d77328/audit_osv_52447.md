# [H] CVE-2021-47458

## Summary
Severity: High
Advisory: CVE-2021-47458
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47458
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: mount fails with buffer overflow in strlen

Starting with kernel 5.11 built with CONFIG_FORTIFY_SOURCE mouting an
ocfs2 filesystem with either o2cb or pcmk cluster stack fails with the
trace below.  Problem seems to be that strings for cluster stack and
cluster name are not guaranteed to be null terminated in the disk
representation, while strlcpy assumes that the source string is always
null terminated.  This causes a read outside of the source string
triggering the buffer overflow detection.

  detected buffer overflow in strlen
  ------------[ cut here ]------------
  kernel BUG at lib/string.c:1149!
  invalid opcode: 0000 [#1] SMP PTI
  CPU: 1 PID: 910 Comm: mount.ocfs2 Not tainted 5.14.0-1-amd64 #1
    Debian 5.14.6-2
  RIP: 0010:fortify_panic+0xf/0x11
  ...
  Call Trace:
   ocfs2_initialize_super.isra.0.cold+0xc/0x18 [ocfs2]
   ocfs2_fill_super+0x359/0x19b0 [ocfs2]
   mount_bdev+0x185/0x1b0
   legacy_get_tree+0x27/0x40
   vfs_get_tree+0x25/0xb0
   path_mount+0x454/0xa20
   __x64_sys_mount+0x103/0x140
   do_syscall_64+0x3b/0xc0
   entry_SYSCALL_64_after_hwframe+0x44/0xae

## References
- https://git.kernel.org/stable/c/0e677ea5b7396f715a76b6b0ef441430e4c4b57f
- https://git.kernel.org/stable/c/232ed9752510de4436468b653d145565669c8498
- https://git.kernel.org/stable/c/4b74ddcc22ee6455946e80a9c4808801f8f8561e
- https://git.kernel.org/stable/c/7623b1035ca2d17bde0f6a086ad6844a34648df1
- https://git.kernel.org/stable/c/93be0eeea14cf39235e585c8f56df3b3859deaad
- https://git.kernel.org/stable/c/ac011cb3ff7a76b3e0e6e77158ee4ba2f929e1fb
- https://git.kernel.org/stable/c/b15fa9224e6e1239414525d8d556d824701849fc
- https://git.kernel.org/stable/c/d3a83576378b4c904f711598dde2c5e881c4295c
