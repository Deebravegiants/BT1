# [H] net/sched: Enforce that teql can only be used as root qdisc

## Summary
Severity: High
Advisory: CVE-2026-23074
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-23074
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.249, >=5.11.0 <5.15.199, >=5.16.0 <6.1.162, >=6.2.0 <6.6.122, >=6.7.0 <6.12.68, >=6.13.0 <6.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: Enforce that teql can only be used as root qdisc

Design intent of teql is that it is only supposed to be used as root qdisc.
We need to check for that constraint.

Although not important, I will describe the scenario that unearthed this
issue for the curious.

GangMin Kim <km.kim1503@gmail.com> managed to concot a scenario as follows:

ROOT qdisc 1:0 (QFQ)
  ├── class 1:1 (weight=15, lmax=16384) netem with delay 6.4s
  └── class 1:2 (weight=1, lmax=1514) teql

GangMin sends a packet which is enqueued to 1:1 (netem).
Any invocation of dequeue by QFQ from this class will not return a packet
until after 6.4s. In the meantime, a second packet is sent and it lands on
1:2. teql's enqueue will return success and this will activate class 1:2.
Main issue is that teql only updates the parent visible qlen (sch->q.qlen)
at dequeue. Since QFQ will only call dequeue if peek succeeds (and teql's
peek always returns NULL), dequeue will never be called and thus the qlen
will remain as 0. With that in mind, when GangMin updates 1:2's lmax value,
the qfq_change_class calls qfq_deact_rm_from_agg. Since the child qdisc's
qlen was not incremented, qfq fails to deactivate the class, but still
frees its pointers from the aggregate. So when the first packet is
rescheduled after 6.4 seconds (netem's delay), a dangling pointer is
accessed causing GangMin's causing a UAF.

## References
- https://git.kernel.org/stable/c/0686bedfed34155520f3f735cbf3210cb9044380
- https://git.kernel.org/stable/c/16ed73c1282d376b956bff23e5139add061767ba
- https://git.kernel.org/stable/c/4c7e8aa71c9232cba84c289b4b56cba80b280841
- https://git.kernel.org/stable/c/50da4b9d07a7a463e2cfb738f3ad4cff6b2c9c3b
- https://git.kernel.org/stable/c/73d970ff0eddd874a84c953387c7f4464b705fc6
- https://git.kernel.org/stable/c/ae810e6a8ac4fe25042e6825d2a401207a2e41fb
- https://git.kernel.org/stable/c/dad49a67c2d817bfec98e6e45121b351e3a0202c
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-23074.json
- https://access.redhat.com/errata/RHSA-2026:3083
- https://access.redhat.com/errata/RHSA-2026:3110
- https://access.redhat.com/errata/RHSA-2026:3268
- https://access.redhat.com/errata/RHSA-2026:3277
- https://access.redhat.com/errata/RHSA-2026:3360
- https://access.redhat.com/errata/RHSA-2026:3388
- https://access.redhat.com/errata/RHSA-2026:3634
- https://access.redhat.com/errata/RHSA-2026:3685
- https://access.redhat.com/errata/RHSA-2026:3810
- https://access.redhat.com/security/cve/CVE-2026-23074
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23074.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23074
