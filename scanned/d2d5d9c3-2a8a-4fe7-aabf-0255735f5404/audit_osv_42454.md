# [C] mptcp: fix stale skb->sk reference on subflow close

## Summary
Severity: Critical
Advisory: CVE-2026-68170
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68170
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: fix stale skb->sk reference on subflow close

The backlog list is updated by mptcp_data_ready() under
mptcp_data_lock(). The cleanup of backlog references to a closing
subflow, however, was performed in mptcp_close_ssk(), before
__mptcp_close_ssk() acquires the ssk lock, and while holding neither
the ssk lock nor mptcp_data_lock().

Because that traversal ran without mptcp_data_lock(), concurrent softirq
RX processing on another CPU (subflow_data_ready() -> mptcp_data_ready()
-> __mptcp_add_backlog(), under mptcp_data_lock()) could add a backlog
entry referencing the ssk while the cleanup loop was in progress. Such
an entry could be missed by the cleanup, or the concurrent list update
could corrupt the traversal, leaving skb->sk pointing at the ssk after
it is freed.

A later mptcp_backlog_purge() then dereferences the stale pointer,
triggering a warning in inet_sock_destruct() (ssk->sk_rmem_alloc != 0)
followed by a use-after-free in mptcp_backlog_purge().

Fix this by moving the backlog cleanup into __mptcp_close_ssk(), after
subflow->closing is set to 1 and while the ssk lock is still held,
serialized under mptcp_data_lock(). The cleanup runs only on the push
path (MPTCP_CF_PUSH), where backlog references accumulate; on other
teardown paths the caller already handles cleanup.

With subflow->closing set and mptcp_data_lock() held across the purge,
any concurrent mptcp_data_ready() either completes its enqueue before
the purge runs and is caught, or observes closing=1 and bails out. Once
mptcp_data_unlock() is reached, no new skb referencing the ssk can be
enqueued, so the cleanup is exhaustive.

Remove the unprotected traversal from mptcp_close_ssk() entirely.

## References
- https://git.kernel.org/stable/c/625fc6060864889fe3d370cdeffbbab762af3cb4
- https://git.kernel.org/stable/c/bd7aae448f6ee9d82599a4474664de1e6e91a535
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68170.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68170
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
