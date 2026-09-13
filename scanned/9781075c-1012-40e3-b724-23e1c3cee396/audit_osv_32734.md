# [H] codel: remove sch->q.qlen check before qdisc_tree_reduce_backlog()

## Summary
Severity: High
Advisory: CVE-2025-37798
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2025-37798
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

codel: remove sch->q.qlen check before qdisc_tree_reduce_backlog()

After making all ->qlen_notify() callbacks idempotent, now it is safe to
remove the check of qlen!=0 from both fq_codel_dequeue() and
codel_qdisc_dequeue().

## References
- https://git.kernel.org/stable/c/2f9761a94bae33d26e6a81b31b36e7d776d93dc1
- https://git.kernel.org/stable/c/342debc12183b51773b3345ba267e9263bdfaaef
- https://git.kernel.org/stable/c/4d55144b12e742404bb3f8fee6038bafbf45619d
- https://git.kernel.org/stable/c/7a742a9506849d1c1aa71e36c89855ceddc7d58e
- https://git.kernel.org/stable/c/829c49b6b2ff45b043739168fd1245e4e1a91a30
- https://git.kernel.org/stable/c/a57fe60ef4cf96bfbb6b58397ec28bdb5a5c6b31
- https://git.kernel.org/stable/c/cc71a757da78dd4aa1b4a9b19cb011833730ccf2
- https://git.kernel.org/stable/c/e73c838c80dccb9e4f19becc11d9f3cb4a27d483
- https://git.kernel.org/stable/c/eda741fe155ddf5ecd2dd3bfbd4fc3c0c7dbb450
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37798.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37798
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
