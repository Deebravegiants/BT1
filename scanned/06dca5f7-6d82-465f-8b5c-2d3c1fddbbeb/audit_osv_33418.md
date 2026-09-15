# [C] smb: client: fix potential cfid UAF in smb2_query_info_compound

## Summary
Severity: Critical
Advisory: CVE-2025-40320
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-40320
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.117, >=6.7.0 <6.12.58, >=6.8.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix potential cfid UAF in smb2_query_info_compound

When smb2_query_info_compound() retries, a previously allocated cfid may
have been freed in the first attempt.
Because cfid wasn't reset on replay, later cleanup could act on a stale
pointer, leading to a potential use-after-free.

Reinitialize cfid to NULL under the replay label.

Example trace (trimmed):

refcount_t: underflow; use-after-free.
WARNING: CPU: 1 PID: 11224 at ../lib/refcount.c:28 refcount_warn_saturate+0x9c/0x110
[...]
RIP: 0010:refcount_warn_saturate+0x9c/0x110
[...]
Call Trace:
 <TASK>
 smb2_query_info_compound+0x29c/0x5c0 [cifs f90b72658819bd21c94769b6a652029a07a7172f]
 ? step_into+0x10d/0x690
 ? __legitimize_path+0x28/0x60
 smb2_queryfs+0x6a/0xf0 [cifs f90b72658819bd21c94769b6a652029a07a7172f]
 smb311_queryfs+0x12d/0x140 [cifs f90b72658819bd21c94769b6a652029a07a7172f]
 ? kmem_cache_alloc+0x18a/0x340
 ? getname_flags+0x46/0x1e0
 cifs_statfs+0x9f/0x2b0 [cifs f90b72658819bd21c94769b6a652029a07a7172f]
 statfs_by_dentry+0x67/0x90
 vfs_statfs+0x16/0xd0
 user_statfs+0x54/0xa0
 __do_sys_statfs+0x20/0x50
 do_syscall_64+0x58/0x80

## References
- https://git.kernel.org/stable/c/327f89c21601ebb7889f8c97754b76f08ce95a0c
- https://git.kernel.org/stable/c/5c76f9961c170552c1d07c830b5e145475151600
- https://git.kernel.org/stable/c/939c4e33005e2a56ea8fcedddf0da92df864bd3b
- https://git.kernel.org/stable/c/b556c278d43f4707a9073ca74d55581b4f279806
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40320.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40320
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
