# [H] NFSD: Defer sub-object cleanup in export put callbacks

## Summary
Severity: High
Advisory: CVE-2026-31404
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-31404
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Defer sub-object cleanup in export put callbacks

svc_export_put() calls path_put() and auth_domain_put() immediately
when the last reference drops, before the RCU grace period. RCU
readers in e_show() and c_show() access both ex_path (via
seq_path/d_path) and ex_client->name (via seq_escape) without
holding a reference. If cache_clean removes the entry and drops the
last reference concurrently, the sub-objects are freed while still
in use, producing a NULL pointer dereference in d_path.

Commit 2530766492ec ("nfsd: fix UAF when access ex_uuid or
ex_stats") moved kfree of ex_uuid and ex_stats into the
call_rcu callback, but left path_put() and auth_domain_put() running
before the grace period because both may sleep and call_rcu
callbacks execute in softirq context.

Replace call_rcu/kfree_rcu with queue_rcu_work(), which defers the
callback until after the RCU grace period and executes it in process
context where sleeping is permitted. This allows path_put() and
auth_domain_put() to be moved into the deferred callback alongside
the other resource releases. Apply the same fix to expkey_put(),
which has the identical pattern with ek_path and ek_client.

A dedicated workqueue scopes the shutdown drain to only NFSD
export release work items; flushing the shared
system_unbound_wq would stall on unrelated work from other
subsystems. nfsd_export_shutdown() uses rcu_barrier() followed
by flush_workqueue() to ensure all deferred release callbacks
complete before the export caches are destroyed.

Reviwed-by: Jeff Layton <jlayton@kernel.org>

## References
- https://git.kernel.org/stable/c/2829e80d29b627886d12b5ea40856d56b516e67d
- https://git.kernel.org/stable/c/48db892356d6cb80f6942885545de4a6dd8d2a29
- https://git.kernel.org/stable/c/f5ab1bec5fa18731e0b1b1e60c9a68667ac73ea2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31404.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31404
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
