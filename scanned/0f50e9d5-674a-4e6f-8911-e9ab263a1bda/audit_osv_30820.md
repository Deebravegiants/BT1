# [M] wifi: brcmfmac: Fix oops due to NULL pointer dereference in brcmf_sdiod_sglist_rw()

## Summary
Severity: Medium
Advisory: CVE-2024-56593
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56593
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: brcmfmac: Fix oops due to NULL pointer dereference in brcmf_sdiod_sglist_rw()

This patch fixes a NULL pointer dereference bug in brcmfmac that occurs
when a high 'sd_sgentry_align' value applies (e.g. 512) and a lot of queued SKBs
are sent from the pkt queue.

The problem is the number of entries in the pre-allocated sgtable, it is
nents = max(rxglom_size, txglom_size) + max(rxglom_size, txglom_size) >> 4 + 1.
Given the default [rt]xglom_size=32 it's actually 35 which is too small.
Worst case, the pkt queue can end up with 64 SKBs. This occurs when a new SKB
is added for each original SKB if tailroom isn't enough to hold tail_pad.
At least one sg entry is needed for each SKB. So, eventually the "skb_queue_walk loop"
in brcmf_sdiod_sglist_rw may run out of sg entries. This makes sg_next return
NULL and this causes the oops.

The patch sets nents to max(rxglom_size, txglom_size) * 2 to be able handle
the worst-case.
Btw. this requires only 64-35=29 * 16 (or 20 if CONFIG_NEED_SG_DMA_LENGTH) = 464
additional bytes of memory.

## References
- https://git.kernel.org/stable/c/07c020c6d14d29e5a3ea4e4576b8ecf956a80834
- https://git.kernel.org/stable/c/342f87d263462c2670b77ea9a32074cab2ac6fa1
- https://git.kernel.org/stable/c/34941321b516bd7c6103bd01287d71a1804d19d3
- https://git.kernel.org/stable/c/67a25ea28f8ec1da8894f2f115d01d3becf67dc7
- https://git.kernel.org/stable/c/7522d7d745d13fbeff3350fe6aa56c8dae263571
- https://git.kernel.org/stable/c/857282b819cbaa0675aaab1e7542e2c0579f52d7
- https://git.kernel.org/stable/c/dfb3f9d3f602602de208da7bdcc0f6d5ee74af68
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56593.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56593
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
