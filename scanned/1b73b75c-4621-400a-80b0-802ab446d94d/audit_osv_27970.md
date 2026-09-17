# [H] aoe: fix the potential use-after-free problem in aoecmd_cfg_pkts

## Summary
Severity: High
Advisory: CVE-2024-26898
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26898
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <4.19.311, >=4.20.0 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

aoe: fix the potential use-after-free problem in aoecmd_cfg_pkts

This patch is against CVE-2023-6270. The description of cve is:

  A flaw was found in the ATA over Ethernet (AoE) driver in the Linux
  kernel. The aoecmd_cfg_pkts() function improperly updates the refcnt on
  `struct net_device`, and a use-after-free can be triggered by racing
  between the free on the struct and the access through the `skbtxq`
  global queue. This could lead to a denial of service condition or
  potential code execution.

In aoecmd_cfg_pkts(), it always calls dev_put(ifp) when skb initial
code is finished. But the net_device ifp will still be used in
later tx()->dev_queue_xmit() in kthread. Which means that the
dev_put(ifp) should NOT be called in the success path of skb
initial code in aoecmd_cfg_pkts(). Otherwise tx() may run into
use-after-free because the net_device is freed.

This patch removed the dev_put(ifp) in the success path in
aoecmd_cfg_pkts(), and added dev_put() after skb xmit in tx().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://git.kernel.org/stable/c/079cba4f4e307c69878226fdf5228c20aa1c969c
- https://git.kernel.org/stable/c/1a54aa506b3b2f31496731039e49778f54eee881
- https://git.kernel.org/stable/c/74ca3ef68d2f449bc848c0a814cefc487bf755fa
- https://git.kernel.org/stable/c/7dd09fa80b0765ce68bfae92f4e2f395ccf0fba4
- https://git.kernel.org/stable/c/a16fbb80064634b254520a46395e36b87ca4731e
- https://git.kernel.org/stable/c/ad80c34944d7175fa1f5c7a55066020002921a99
- https://git.kernel.org/stable/c/eb48680b0255a9e8a9bdc93d6a55b11c31262e62
- https://git.kernel.org/stable/c/f98364e926626c678fb4b9004b75cacf92ff0662
- https://git.kernel.org/stable/c/faf0b4c5e00bb680e8e43ac936df24d3f48c8e65
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26898.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26898
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
