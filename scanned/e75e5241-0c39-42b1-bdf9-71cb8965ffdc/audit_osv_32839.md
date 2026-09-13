# [H] net_sched: ets: fix a race in ets_qdisc_change()

## Summary
Severity: High
Advisory: CVE-2025-38107
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38107
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.0.0 <6.6.94, >=6.2.0 <6.12.34, >=6.7.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net_sched: ets: fix a race in ets_qdisc_change()

Gerrard Tai reported a race condition in ETS, whenever SFQ perturb timer
fires at the wrong time.

The race is as follows:

CPU 0                                 CPU 1
[1]: lock root
[2]: qdisc_tree_flush_backlog()
[3]: unlock root
 |
 |                                    [5]: lock root
 |                                    [6]: rehash
 |                                    [7]: qdisc_tree_reduce_backlog()
 |
[4]: qdisc_put()

This can be abused to underflow a parent's qlen.

Calling qdisc_purge_queue() instead of qdisc_tree_flush_backlog()
should fix the race, because all packets will be purged from the qdisc
before releasing the lock.

## References
- https://git.kernel.org/stable/c/0383b25488a545be168744336847549d4a2d3d6c
- https://git.kernel.org/stable/c/073f64c03516bcfaf790f8edc772e0cfb8a84ec3
- https://git.kernel.org/stable/c/0b479d0aa488cb478eb2e1d8868be946ac8afb4f
- https://git.kernel.org/stable/c/347867cb424edae5fec1622712c8dd0a2c42918f
- https://git.kernel.org/stable/c/d92adacdd8c2960be856e0b82acc5b7c5395fddb
- https://git.kernel.org/stable/c/eb7b74e9754e1ba2088f914ad1f57a778b11894b
- https://git.kernel.org/stable/c/fed94bd51d62d2e0e006aa61480e94e5cd0582b0
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38107.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38107
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
