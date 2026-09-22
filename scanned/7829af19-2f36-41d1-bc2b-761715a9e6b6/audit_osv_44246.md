# [C] netfilter: nf_conntrack_expect: use conntrack GC to reap expectations

## Summary
Severity: Critical
Advisory: CVE-2026-80668
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80668
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conntrack_expect: use conntrack GC to reap expectations

This patch replaces the timer API by GC worker approach for
expectations, as it already happened in many other subsystems.

Use the existing conntrack GC worker to iterate over the local list of
expectations in the master conntrack to reap expired expectations.
Check IPS_HELPER_BIT to run GC for expectations, set it on for nft_ct
expectation which nevers sets it. Hold the expectation spinlock while
iterating over the master conntrack expectation list to synchronize with
nf_ct_remove_expectations(). This also performs runtime packet path
garbage collection through the expectation insertion and lookup
functions while walking over one of the chains of the global expectation
hashtables. Unconfirmed conntrack entries are skipped since ct->ext can
be reallocated and dying are skipped since those will be gone soon.
Set on IPS_HELPER_BIT if the helper ct extension is added, then the new
GC worker does not need to bump the ct refcount to check if the ct->ext
helper is available.

This removes the extra bump on the refcount for expectation timers, this
allows to remove several nf_ct_expect_put() calls after the unlink,
after this update only refcount remains at 1 while on the expectation
hashes.

This patch implicitly addresses a race with the existing timer API
allowing an expectation to access a stale exp->master pointer which has
been already released when expectation removal loses races with an
expiring timer, ie. timer_del() reporting false.

Add a new NF_CT_EXPECT_DEAD flag to reap this expectation via GC. This
is needed by nf_conntrack_unexpect_related() which is called in error
paths to invalidate newly created expectations that has been added into
the hashes. These expectactions cannot be inmediately released as GC or
nf_ct_remove_expectations() could race to make it. On expectation
insert, the runtime GC reaps stale expectations before checking the
expectation limit set by policy.

Set current timestamp in nf_ct_expect_alloc(), then add the expectation
policy timeout (or custom timeout specified added on top of this) to
specify the expectation lifetime.

## References
- https://git.kernel.org/stable/c/7ec786f4230c2a9b2eaf97a2d45368933b49d2b2
- https://git.kernel.org/stable/c/b8b09dc2bf35a00d4e0556b5d6308c7b917ebda2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80668.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80668
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
