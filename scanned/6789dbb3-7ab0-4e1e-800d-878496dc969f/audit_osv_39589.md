# [H] sctp: revalidate list cursor after sctp_sendmsg_to_asoc() in SCTP_SENDALL

## Summary
Severity: High
Advisory: CVE-2026-46227
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46227
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.90, >=6.13.0 <6.18.32, >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: revalidate list cursor after sctp_sendmsg_to_asoc() in SCTP_SENDALL

The SCTP_SENDALL path in sctp_sendmsg() iterates ep->asocs with
list_for_each_entry_safe(), which caches the next entry in @tmp before
the loop body runs.  The body calls sctp_sendmsg_to_asoc(), which may
drop the socket lock inside sctp_wait_for_sndbuf().

While the lock is dropped, another thread can SCTP_SOCKOPT_PEELOFF the
association cached in @tmp, migrating it to a new endpoint via
sctp_sock_migrate() (list_del_init() + list_add_tail() to
newep->asocs), and optionally close the new socket which frees the
association via kfree_rcu().  The cached @tmp can also be freed by a
network ABORT for that association, processed in softirq while the
lock is dropped.

sctp_wait_for_sndbuf() revalidates @asoc (the current entry) on re-lock
via the "sk != asoc->base.sk" and "asoc->base.dead" checks, but nothing
revalidates @tmp.  After a successful return, the iterator advances to
the stale @tmp, yielding either a use-after-free (if the peeled socket
was closed) or a list-walk onto the new endpoint's list head (type
confusion of &newep->asocs as a struct sctp_association *).

Both are reachable from CapEff=0; the type-confusion path gives
controlled indirect call via the outqueue.sched->init_sid pointer.

Fix by re-deriving @tmp from @asoc after sctp_sendmsg_to_asoc()
returns.  @asoc is known to still be on ep->asocs at that point: the
only callers that list_del an association from ep->asocs are
sctp_association_free() (which sets asoc->base.dead) and
sctp_assoc_migrate() (which changes asoc->base.sk), and
sctp_wait_for_sndbuf() checks both under the lock before any
successful return; a tripped check propagates as err < 0 and the loop
bails before the re-derive.

The SCTP_ABORT path in sctp_sendmsg_check_sflags() returns 0 and the
loop hits 'continue' before sctp_sendmsg_to_asoc() is ever called, so
the @tmp cached by list_for_each_entry_safe() still covers the
lock-held free that ba59fb027307 ("sctp: walk the list of asoc
safely") was added for.

## References
- https://git.kernel.org/stable/c/0c7b55974f97b78d1109025eadf084e74cbf330f
- https://git.kernel.org/stable/c/0dbc8cde64280fc37cdd678cced34eaf96cfb197
- https://git.kernel.org/stable/c/1bfb06ecb00f7fdf35dba8e8f2877346cbe5e078
- https://git.kernel.org/stable/c/6187a172d6ed57d6b2c327836e4407c6456e639d
- https://git.kernel.org/stable/c/abb5f36771cc4c05899b34000829a787572a8817
- https://git.kernel.org/stable/c/bf0f40d8107e2ce827521968dc6926f3e13728ae
- https://git.kernel.org/stable/c/c9dadb31f36045a8cb65df4bd75e7237ef21a4b5
- https://git.kernel.org/stable/c/f3a3f0b406b4b7eb3cea35a23fa2bf170848b104
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46227.json
- https://access.redhat.com/errata/RHSA-2026:26462
- https://access.redhat.com/errata/RHSA-2026:26515
- https://access.redhat.com/errata/RHSA-2026:26535
- https://access.redhat.com/errata/RHSA-2026:26563
- https://access.redhat.com/errata/RHSA-2026:27731
- https://access.redhat.com/errata/RHSA-2026:27735
- https://access.redhat.com/errata/RHSA-2026:33899
- https://access.redhat.com/errata/RHSA-2026:34094
- https://access.redhat.com/errata/RHSA-2026:36018
- https://access.redhat.com/errata/RHSA-2026:36348
- https://access.redhat.com/errata/RHSA-2026:36349
