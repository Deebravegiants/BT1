# [H] netfilter: nf_conntrack: defer invalid log until after unlock

## Summary
Severity: High
Advisory: CVE-2026-74624
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74624
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.184, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conntrack: defer invalid log until after unlock

TCP and SCTP conntrack paths can emit invalid-packet logs while ct->lock
is still held.

When invalid logging is routed to nfnetlink_log and conntrack export is
enabled, the log path can re-enter conntrack netlink glue and dump the
same conntrack again. Protocol attribute dumping may take ct->lock, so
logging while holding that lock can deadlock.

Defer the TCP invalid logs by storing only the minimal log context while
ct->lock is held and emitting the log after unlocking. Also make the TCP
timeout-lowering invalid path return whether a log is needed, then emit
that log after unlocking.

Do the same for the SCTP invalid state-transition log that can be reached
while ct->lock is held.

Add a lockdep assertion to nf_ct_l4proto_log_invalid() so future callers
that log invalid conntracks while holding ct->lock are caught outside TCP
and SCTP as well.

## References
- https://git.kernel.org/stable/c/0424186d570aa4d1ad17f516afb86bd9eaa4f42e
- https://git.kernel.org/stable/c/2d19b95c9723001f214f7a47d67b09f46238f200
- https://git.kernel.org/stable/c/63853eb20bba4e00b7cd0b8cfc19337bbaaf5037
- https://git.kernel.org/stable/c/9480fcf70a5aa9d320088a01c95df0e5e6391f4a
- https://git.kernel.org/stable/c/c0224327b7cbed9d3198e8dbec847281053dcd06
- https://git.kernel.org/stable/c/ca97360eba4b3dc67f1804625542f4ccc774242a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74624.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74624
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
