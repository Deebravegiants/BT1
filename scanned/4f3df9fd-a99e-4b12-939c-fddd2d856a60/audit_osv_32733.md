# [H] net_sched: hfsc: Fix a UAF vulnerability in class handling

## Summary
Severity: High
Advisory: CVE-2025-37797
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2025-37797
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.4.293, >=5.5.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.136, >=6.2.0 <6.6.89, >=6.7.0 <6.12.26, >=6.13.0 <6.14.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net_sched: hfsc: Fix a UAF vulnerability in class handling

This patch fixes a Use-After-Free vulnerability in the HFSC qdisc class
handling. The issue occurs due to a time-of-check/time-of-use condition
in hfsc_change_class() when working with certain child qdiscs like netem
or codel.

The vulnerability works as follows:
1. hfsc_change_class() checks if a class has packets (q.qlen != 0)
2. It then calls qdisc_peek_len(), which for certain qdiscs (e.g.,
   codel, netem) might drop packets and empty the queue
3. The code continues assuming the queue is still non-empty, adding
   the class to vttree
4. This breaks HFSC scheduler assumptions that only non-empty classes
   are in vttree
5. Later, when the class is destroyed, this can lead to a Use-After-Free

The fix adds a second queue length check after qdisc_peek_len() to verify
the queue wasn't emptied.

## References
- https://git.kernel.org/stable/c/20d584a33e480ae80d105f43e0e7b56784da41b9
- https://git.kernel.org/stable/c/28b09a067831f7317c3841812276022d6c940677
- https://git.kernel.org/stable/c/39b9095dd3b55d9b2743df038c32138efa34a9de
- https://git.kernel.org/stable/c/3aa852e3605000d5c47035c3fc3a986d14ccfa9f
- https://git.kernel.org/stable/c/3df275ef0a6ae181e8428a6589ef5d5231e58b5c
- https://git.kernel.org/stable/c/86cd4641c713455a4f1c8e54c370c598c2b1cee0
- https://git.kernel.org/stable/c/bb583c88d23b72d8d16453d24856c99bd93dadf5
- https://git.kernel.org/stable/c/fcc8ede663569c704fb00a702973bd6c00373283
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37797.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37797
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
