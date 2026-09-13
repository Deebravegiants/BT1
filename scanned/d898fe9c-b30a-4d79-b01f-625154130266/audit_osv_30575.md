# [H] SUNRPC: make sure cache entry active before cache_show

## Summary
Severity: High
Advisory: CVE-2024-53174
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53174
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

SUNRPC: make sure cache entry active before cache_show

The function `c_show` was called with protection from RCU. This only
ensures that `cp` will not be freed. Therefore, the reference count for
`cp` can drop to zero, which will trigger a refcount use-after-free
warning when `cache_get` is called. To resolve this issue, use
`cache_get_rcu` to ensure that `cp` remains active.

------------[ cut here ]------------
refcount_t: addition on 0; use-after-free.
WARNING: CPU: 7 PID: 822 at lib/refcount.c:25
refcount_warn_saturate+0xb1/0x120
CPU: 7 UID: 0 PID: 822 Comm: cat Not tainted 6.12.0-rc3+ #1
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS
1.16.1-2.fc37 04/01/2014
RIP: 0010:refcount_warn_saturate+0xb1/0x120

Call Trace:
 <TASK>
 c_show+0x2fc/0x380 [sunrpc]
 seq_read_iter+0x589/0x770
 seq_read+0x1e5/0x270
 proc_reg_read+0xe1/0x140
 vfs_read+0x125/0x530
 ksys_read+0xc1/0x160
 do_syscall_64+0x5f/0x170
 entry_SYSCALL_64_after_hwframe+0x76/0x7e

## References
- https://git.kernel.org/stable/c/02999e135b013d85c6df738746e8e24699befee4
- https://git.kernel.org/stable/c/068c0b50f3f700b94f78850834cd91ae3b34c2c1
- https://git.kernel.org/stable/c/2862eee078a4d2d1f584e7f24fa50dddfa5f3471
- https://git.kernel.org/stable/c/acfaf37888e0f0732fb6a50ff093dce6d99994d0
- https://git.kernel.org/stable/c/c7dac3af57e38b2054f990e573256d90bf887958
- https://git.kernel.org/stable/c/d882e2b7fad3f5e5fac66184a347f408813f654a
- https://git.kernel.org/stable/c/e9be26735d055c42543a4d047a769cc6d0fb1504
- https://git.kernel.org/stable/c/ec305f303bf070b4f6896b7a76009f702956d402
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53174.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53174
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
