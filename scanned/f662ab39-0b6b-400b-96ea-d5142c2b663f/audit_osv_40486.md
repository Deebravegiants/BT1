# [C] net: rds: clear i_sends on setup unwind

## Summary
Severity: Critical
Advisory: CVE-2026-53355
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-53355
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: rds: clear i_sends on setup unwind

The RDS IB connection teardown path is written so it can run during
partial startup and on repeated shutdown attempts. It uses NULL
pointers to distinguish resources that are still owned from resources
that have already been released.

When rds_ib_setup_qp() fails after allocating i_sends but before
allocating i_recvs, the sends_out path frees i_sends without clearing
the pointer. A later shutdown pass can still treat that stale pointer
as a live send ring allocation.

Clear i_sends after vfree() in the error unwind path so the existing
shutdown logic continues to use the correct ownership state.

## References
- https://git.kernel.org/stable/c/1d4ec754ee3871f7e3670c67bb0298c9c5760926
- https://git.kernel.org/stable/c/20cf0fb715c41111469577e85e35d15f099473e0
- https://git.kernel.org/stable/c/27040bbca289a704eafcacca167d310c6ce2b1bc
- https://git.kernel.org/stable/c/29d940026dce39e3018dab6f67c9427249321270
- https://git.kernel.org/stable/c/2c5e5e4a5970c41f16e3ad801a78719ed5d5c71b
- https://git.kernel.org/stable/c/66cccec111421a10efdc2c74499d15b93e7acae5
- https://git.kernel.org/stable/c/e7cf30aa5f1fc6c2a86df65df8b731df20e44d79
- https://git.kernel.org/stable/c/f16ad421a4e3e7db2d14bdf3b16f583bc4f3b30a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53355.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53355
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
