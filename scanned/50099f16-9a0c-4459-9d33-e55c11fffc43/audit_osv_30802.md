# [H] nfsd: make sure exp active before svc_export_show

## Summary
Severity: High
Advisory: CVE-2024-56558
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56558
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.17.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: make sure exp active before svc_export_show

The function `e_show` was called with protection from RCU. This only
ensures that `exp` will not be freed. Therefore, the reference count for
`exp` can drop to zero, which will trigger a refcount use-after-free
warning when `exp_get` is called. To resolve this issue, use
`cache_get_rcu` to ensure that `exp` remains active.

------------[ cut here ]------------
refcount_t: addition on 0; use-after-free.
WARNING: CPU: 3 PID: 819 at lib/refcount.c:25
refcount_warn_saturate+0xb1/0x120
CPU: 3 UID: 0 PID: 819 Comm: cat Not tainted 6.12.0-rc3+ #1
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS
1.16.1-2.fc37 04/01/2014
RIP: 0010:refcount_warn_saturate+0xb1/0x120
...
Call Trace:
 <TASK>
 e_show+0x20b/0x230 [nfsd]
 seq_read_iter+0x589/0x770
 seq_read+0x1e5/0x270
 vfs_read+0x125/0x530
 ksys_read+0xc1/0x160
 do_syscall_64+0x5f/0x170
 entry_SYSCALL_64_after_hwframe+0x76/0x7e

## References
- https://git.kernel.org/stable/c/1cecfdbc6bfc89c516d286884c7f29267b95de2b
- https://git.kernel.org/stable/c/6cefcadd34e3c71c81ea64b899a0daa86314a51a
- https://git.kernel.org/stable/c/7365d1f8de63cffdbbaa2287ce0205438e1a922f
- https://git.kernel.org/stable/c/7d8f7816bebcd2e7400bb4d786eccb8f33c9f9ec
- https://git.kernel.org/stable/c/7fd29d284b55c2274f7a748e6c5f25b4758b8da5
- https://git.kernel.org/stable/c/be8f982c369c965faffa198b46060f8853e0f1f0
- https://git.kernel.org/stable/c/e2fa0d0e327279a8defb87b263cd0bf288fd9261
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56558.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56558
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
