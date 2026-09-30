# [H] NFSv4.2: fix nfs4_listxattr kernel BUG at mm/usercopy.c:102

## Summary
Severity: High
Advisory: CVE-2024-26870
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26870
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSv4.2: fix nfs4_listxattr kernel BUG at mm/usercopy.c:102

A call to listxattr() with a buffer size = 0 returns the actual
size of the buffer needed for a subsequent call. When size > 0,
nfs4_listxattr() does not return an error because either
generic_listxattr() or nfs4_listxattr_nfs4_label() consumes
exactly all the bytes then size is 0 when calling
nfs4_listxattr_nfs4_user() which then triggers the following
kernel BUG:

  [   99.403778] kernel BUG at mm/usercopy.c:102!
  [   99.404063] Internal error: Oops - BUG: 00000000f2000800 [#1] SMP
  [   99.408463] CPU: 0 PID: 3310 Comm: python3 Not tainted 6.6.0-61.fc40.aarch64 #1
  [   99.415827] Call trace:
  [   99.415985]  usercopy_abort+0x70/0xa0
  [   99.416227]  __check_heap_object+0x134/0x158
  [   99.416505]  check_heap_object+0x150/0x188
  [   99.416696]  __check_object_size.part.0+0x78/0x168
  [   99.416886]  __check_object_size+0x28/0x40
  [   99.417078]  listxattr+0x8c/0x120
  [   99.417252]  path_listxattr+0x78/0xe0
  [   99.417476]  __arm64_sys_listxattr+0x28/0x40
  [   99.417723]  invoke_syscall+0x78/0x100
  [   99.417929]  el0_svc_common.constprop.0+0x48/0xf0
  [   99.418186]  do_el0_svc+0x24/0x38
  [   99.418376]  el0_svc+0x3c/0x110
  [   99.418554]  el0t_64_sync_handler+0x120/0x130
  [   99.418788]  el0t_64_sync+0x194/0x198
  [   99.418994] Code: aa0003e3 d000a3e0 91310000 97f49bdb (d4210000)

Issue is reproduced when generic_listxattr() returns 'system.nfs4_acl',
thus calling lisxattr() with size = 16 will trigger the bug.

Add check on nfs4_listxattr() to return ERANGE error when it is
called with size > 0 and the return value is greater than size.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/06e828b3f1b206de08ef520fc46a40b22e1869cb
- https://git.kernel.org/stable/c/23bfecb4d852751d5e403557dd500bb563313baf
- https://git.kernel.org/stable/c/251a658bbfceafb4d58c76b77682c8bf7bcfad65
- https://git.kernel.org/stable/c/4403438eaca6e91f02d272211c4d6b045092396b
- https://git.kernel.org/stable/c/79cdcc765969d23f4e3d6ea115660c3333498768
- https://git.kernel.org/stable/c/80365c9f96015bbf048fdd6c8705d3f8770132bf
- https://git.kernel.org/stable/c/9d52865ff28245fc2134da9f99baff603a24407a
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26870.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26870
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
