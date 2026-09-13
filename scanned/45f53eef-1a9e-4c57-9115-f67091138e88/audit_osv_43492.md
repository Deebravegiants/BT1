# [H] netfilter: nf_dup_netdev: add nf_dev_xmit_recursion*() helpers and use them

## Summary
Severity: High
Advisory: CVE-2026-74260
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74260
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_dup_netdev: add nf_dev_xmit_recursion*() helpers and use them

Update nft_dup and nft_fwd to use the nf_dev_xmit_recursion() helpers.
This patch also disables BH when transmitting the skb to address a
possible migration to different CPU leading to imbalanced decrementation
of the recursion counters.

This is modeled after Florian Westphal's dev_xmit_recursion*() API
available since commit 97cdcf37b57e ("net: place xmit recursion in
softnet data") according to its current state in the tree.

## References
- https://git.kernel.org/stable/c/2354e975932dabb06fad239f07a3b68fd1809737
- https://git.kernel.org/stable/c/edf234f71fb327792196f813048ab8f5bd3bb712
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74260.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74260
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
