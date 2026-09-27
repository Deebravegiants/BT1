# [H] nfsd: provide locking for v4_end_grace

## Summary
Severity: High
Advisory: CVE-2026-22980
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2026-22980
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.161, >=6.2.0 <6.6.121, >=6.7.0 <6.12.66, >=6.13.0 <6.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: provide locking for v4_end_grace

Writing to v4_end_grace can race with server shutdown and result in
memory being accessed after it was freed - reclaim_str_hashtbl in
particularly.

We cannot hold nfsd_mutex across the nfsd4_end_grace() call as that is
held while client_tracking_op->init() is called and that can wait for
an upcall to nfsdcltrack which can write to v4_end_grace, resulting in a
deadlock.

nfsd4_end_grace() is also called by the landromat work queue and this
doesn't require locking as server shutdown will stop the work and wait
for it before freeing anything that nfsd4_end_grace() might access.

However, we must be sure that writing to v4_end_grace doesn't restart
the work item after shutdown has already waited for it.  For this we
add a new flag protected with nn->client_lock.  It is set only while it
is safe to make client tracking calls, and v4_end_grace only schedules
work while the flag is set with the spinlock held.

So this patch adds a nfsd_net field "client_tracking_active" which is
set as described.  Another field "grace_end_forced", is set when
v4_end_grace is written.  After this is set, and providing
client_tracking_active is set, the laundromat is scheduled.
This "grace_end_forced" field bypasses other checks for whether the
grace period has finished.

This resolves a race which can result in use-after-free.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/06600719d0f7a723811c45e4d51f5b742f345309
- https://git.kernel.org/stable/c/2857bd59feb63fcf40fe4baf55401baea6b4feb4
- https://git.kernel.org/stable/c/34eb22836e0cdba093baac66599d68c4cd245a9d
- https://git.kernel.org/stable/c/53f07d095e7e680c5e4569a55a019f2c0348cdc6
- https://git.kernel.org/stable/c/ba4811c8b433bfa681729ca42cc62b6034f223b0
- https://git.kernel.org/stable/c/ca97360860eb02e3ae4ba42c19b439a0fcecbf06
- https://git.kernel.org/stable/c/e8bfa2401d4c51eca6e48e9b33c798828ca9df61
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22980.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22980
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
