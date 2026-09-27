# [H] tipc: avoid use-after-free in poll trace queue dumps

## Summary
Severity: High
Advisory: CVE-2026-74490
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74490
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: avoid use-after-free in poll trace queue dumps

TIPC socket tracepoints dump queue state through tipc_sk_dump(). Most
queue-dump callsites already serialize that walk under the socket lock or
sk->sk_lock.slock, but tipc_poll() calls trace_tipc_sk_poll(...,
TIPC_DUMP_ALL, ...) without holding either lock.

That lets the poll trace path reach tipc_list_dump() and backlog head/tail
dumping while another context dequeues and frees an skb, leaving the trace
helper dereferencing a stale queue entry.

Stop the unlocked poll trace site from requesting queue dumps. Other queue
dump trace callsites keep their existing output under the locking they
already provide, while poll still emits the event itself without walking
live queue members from an unlocked context.

## References
- https://git.kernel.org/stable/c/3cd57c6b210d50fd1f7ac1720442ba5be5dc94f8
- https://git.kernel.org/stable/c/5e82beba4bc1f91d0e64c9c43f2b2fa9cd1c2a7d
- https://git.kernel.org/stable/c/78706367fe1b98aee0a6de27c62b7f1e3035f38d
- https://git.kernel.org/stable/c/ac2f787980fdf4364cd5651a4c8128e59b8de3aa
- https://git.kernel.org/stable/c/ae7fc824970888b4fdaa076819c9a6f2fcede275
- https://git.kernel.org/stable/c/b4f1719dfea023220e0e6bd892b087d76b2a6a49
- https://git.kernel.org/stable/c/bed792737b5f1ba773054dbe984502958bdfe6ce
- https://git.kernel.org/stable/c/d7940bb6a8e7ab28f972c2875cb05783216312dc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74490.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74490
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
