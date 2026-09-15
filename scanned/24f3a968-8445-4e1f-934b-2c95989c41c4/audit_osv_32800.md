# [H] sch_hfsc: Fix qlen accounting bug when using peek in hfsc_enqueue()

## Summary
Severity: High
Advisory: CVE-2025-38000
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-06
Source: https://osv.dev/vulnerability/CVE-2025-38000
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.4.294, >=5.5.0 <5.10.238, >=5.11.0 <5.15.185, >=5.16.0 <6.1.141, >=6.2.0 <6.6.93, >=6.7.0 <6.12.31, >=6.13.0 <6.14.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

sch_hfsc: Fix qlen accounting bug when using peek in hfsc_enqueue()

When enqueuing the first packet to an HFSC class, hfsc_enqueue() calls the
child qdisc's peek() operation before incrementing sch->q.qlen and
sch->qstats.backlog. If the child qdisc uses qdisc_peek_dequeued(), this may
trigger an immediate dequeue and potential packet drop. In such cases,
qdisc_tree_reduce_backlog() is called, but the HFSC qdisc's qlen and backlog
have not yet been updated, leading to inconsistent queue accounting. This
can leave an empty HFSC class in the active list, causing further
consequences like use-after-free.

This patch fixes the bug by moving the increment of sch->q.qlen and
sch->qstats.backlog before the call to the child qdisc's peek() operation.
This ensures that queue length and backlog are always accurate when packet
drops or dequeues are triggered during the peek.

## References
- https://git.kernel.org/stable/c/1034e3310752e8675e313f7271b348914008719a
- https://git.kernel.org/stable/c/3f3a22eebbc32b4fa8ce9c1d5f9db214b45b9335
- https://git.kernel.org/stable/c/3f981138109f63232a5fb7165938d4c945cc1b9d
- https://git.kernel.org/stable/c/49b21795b8e5654a7df3d910a12e1060da4c04cf
- https://git.kernel.org/stable/c/89c301e929a0db14ebd94b4d97764ce1d6981653
- https://git.kernel.org/stable/c/93c276942e75de0e5bc91576300d292e968f5a02
- https://git.kernel.org/stable/c/f1dde3eb17dc1b8bd07aed00004b1e05fc87a3d4
- https://git.kernel.org/stable/c/f9f593e34d2fb67644372c8f7b033bdc622ad228
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38000.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38000
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
