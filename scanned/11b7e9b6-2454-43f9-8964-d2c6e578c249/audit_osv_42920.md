# [H] openrisc: Fix jump_label smp syncing

## Summary
Severity: High
Advisory: CVE-2026-72154
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72154
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

openrisc: Fix jump_label smp syncing

The original commit 8c30b0018f9d ("openrisc: Add jump label support")
copies from arm64 and does not properly consider how icache invalidation
on remote cores works in OpenRISC.  On OpenRISC remote icaches need to
be invalidated otherwise static key's may remain state after updating.

Fix SMP cache syncing by:

 1. Properly invalidate remote core icaches on SMP systems by using
    icache_all_inv.  The old code uses kick_all_cpus_sync() which runs a
    no-op IPI function call on remote CPU's which does execute a lot of
    code and flushes many cache lines in the process, but does not flush
    all and it's not correct on OpenRISC.
 2. For architectures that do not have WRITETHROUGH caches be sure
    to flush the dcache after patching.

To test this I first reproduced the issue using a custom test module
[0].  The test confirmed that some icache lines maintained stale
static_key code sequences after calling static_branch_enable().  After
this patch there are no longer jump_label coherency issues.

[0] https://github.com/stffrdhrn/or1k-utils/tree/master/tests/smp_static_key_test

## References
- https://git.kernel.org/stable/c/3fac46068fe4cea22ed373432b9173a915e8e60d
- https://git.kernel.org/stable/c/57740658042daf591c57d6e700d9a304d5972552
- https://git.kernel.org/stable/c/aca063c9024522e4e5b9a9d1927433f6a01785a3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72154.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72154
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
