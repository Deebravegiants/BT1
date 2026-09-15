# [H] netem: fix return value if duplicate enqueue fails

## Summary
Severity: High
Advisory: CVE-2024-45016
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-11
Source: https://osv.dev/vulnerability/CVE-2024-45016
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.4.283, >=5.5.0 <5.10.225, >=5.11.0 <5.15.166, >=5.16.0 <6.1.107, >=6.2.0 <6.6.48, >=6.7.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

netem: fix return value if duplicate enqueue fails

There is a bug in netem_enqueue() introduced by
commit 5845f706388a ("net: netem: fix skb length BUG_ON in __skb_to_sgvec")
that can lead to a use-after-free.

This commit made netem_enqueue() always return NET_XMIT_SUCCESS
when a packet is duplicated, which can cause the parent qdisc's q.qlen
to be mistakenly incremented. When this happens qlen_notify() may be
skipped on the parent during destruction, leaving a dangling pointer
for some classful qdiscs like DRR.

There are two ways for the bug happen:

- If the duplicated packet is dropped by rootq->enqueue() and then
  the original packet is also dropped.
- If rootq->enqueue() sends the duplicated packet to a different qdisc
  and the original packet is dropped.

In both cases NET_XMIT_SUCCESS is returned even though no packets
are enqueued at the netem qdisc.

The fix is to defer the enqueue of the duplicate packet until after
the original packet has been guaranteed to return NET_XMIT_SUCCESS.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/0486d31dd8198e22b63a4730244b38fffce6d469
- https://git.kernel.org/stable/c/52d99a69f3d556c6426048c9d481b912205919d8
- https://git.kernel.org/stable/c/577d6c0619467fe90f7e8e57e45cb5bd9d936014
- https://git.kernel.org/stable/c/759e3e8c4a6a6b4e52ebc4547123a457f0ce90d4
- https://git.kernel.org/stable/c/c07ff8592d57ed258afee5a5e04991a48dbaf382
- https://git.kernel.org/stable/c/c414000da1c2ea1ba9a5e5bb1a4ba774e51e202d
- https://git.kernel.org/stable/c/e5bb2988a310667abed66c7d3ffa28880cf0f883
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45016.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45016
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
