# [H] net: xilinx: axienet: Fix BQL accounting for multi-BD TX packets

## Summary
Severity: High
Advisory: CVE-2026-43031
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43031
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: xilinx: axienet: Fix BQL accounting for multi-BD TX packets

When a TX packet spans multiple buffer descriptors (scatter-gather),
axienet_free_tx_chain sums the per-BD actual length from descriptor
status into a caller-provided accumulator. That sum is reset on each
NAPI poll. If the BDs for a single packet complete across different
polls, the earlier bytes are lost and never credited to BQL. This
causes BQL to think bytes are permanently in-flight, eventually
stalling the TX queue.

The SKB pointer is stored only on the last BD of a packet. When that
BD completes, use skb->len for the byte count instead of summing
per-BD status lengths. This matches netdev_sent_queue(), which debits
skb->len, and naturally survives across polls because no partial
packet contributes to the accumulator.

## References
- https://git.kernel.org/stable/c/2a0323a913109b52bfc9f5ea7b92a1b249e07d3e
- https://git.kernel.org/stable/c/3c3a6b9020c01fde7b22e8550105de0b59904f61
- https://git.kernel.org/stable/c/d1978d03e86785872871bff9c2623174b10740de
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43031.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43031
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
