# [C] nfs: Fix KMSAN warning in decode_getfattr_attrs()

## Summary
Severity: Critical
Advisory: CVE-2024-53066
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53066
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <4.19.324, >=4.20.0 <5.4.286, >=5.5.0 <5.10.230, >=5.11.0 <5.15.172, >=5.16.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfs: Fix KMSAN warning in decode_getfattr_attrs()

Fix the following KMSAN warning:

CPU: 1 UID: 0 PID: 7651 Comm: cp Tainted: G    B
Tainted: [B]=BAD_PAGE
Hardware name: QEMU Standard PC (Q35 + ICH9, 2009)
=====================================================
=====================================================
BUG: KMSAN: uninit-value in decode_getfattr_attrs+0x2d6d/0x2f90
 decode_getfattr_attrs+0x2d6d/0x2f90
 decode_getfattr_generic+0x806/0xb00
 nfs4_xdr_dec_getattr+0x1de/0x240
 rpcauth_unwrap_resp_decode+0xab/0x100
 rpcauth_unwrap_resp+0x95/0xc0
 call_decode+0x4ff/0xb50
 __rpc_execute+0x57b/0x19d0
 rpc_execute+0x368/0x5e0
 rpc_run_task+0xcfe/0xee0
 nfs4_proc_getattr+0x5b5/0x990
 __nfs_revalidate_inode+0x477/0xd00
 nfs_access_get_cached+0x1021/0x1cc0
 nfs_do_access+0x9f/0xae0
 nfs_permission+0x1e4/0x8c0
 inode_permission+0x356/0x6c0
 link_path_walk+0x958/0x1330
 path_lookupat+0xce/0x6b0
 filename_lookup+0x23e/0x770
 vfs_statx+0xe7/0x970
 vfs_fstatat+0x1f2/0x2c0
 __se_sys_newfstatat+0x67/0x880
 __x64_sys_newfstatat+0xbd/0x120
 x64_sys_call+0x1826/0x3cf0
 do_syscall_64+0xd0/0x1b0
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

The KMSAN warning is triggered in decode_getfattr_attrs(), when calling
decode_attr_mdsthreshold(). It appears that fattr->mdsthreshold is not
initialized.

Fix the issue by initializing fattr->mdsthreshold to NULL in
nfs_fattr_init().

## References
- https://git.kernel.org/stable/c/25ffd294fef81a7f3cd9528adf21560c04d98747
- https://git.kernel.org/stable/c/8fc5ea9231af9122d227c9c13f5e578fca48d2e3
- https://git.kernel.org/stable/c/9b453e8b108a5a93a6e348cf2ba4c9c138314a00
- https://git.kernel.org/stable/c/9be0a21ae52b3b822d0eec4d14e909ab394f8a92
- https://git.kernel.org/stable/c/bbfcd261cc068fe1cd02a4e871275074a0daa4e2
- https://git.kernel.org/stable/c/dc270d7159699ad6d11decadfce9633f0f71c1db
- https://git.kernel.org/stable/c/f6b2b2b981af8e7d7c62d34143acefa4e1edfe8b
- https://git.kernel.org/stable/c/f749cb60a01f8391c760a1d6ecd938cadacf9549
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53066.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53066
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
