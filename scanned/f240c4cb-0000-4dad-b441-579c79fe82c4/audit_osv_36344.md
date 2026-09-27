# [H] net: wwan: t7xx: fix potential skb->frags overflow in RX path

## Summary
Severity: High
Advisory: CVE-2026-23172
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2026-23172
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.162, >=6.2.0 <6.6.123, >=6.7.0 <6.12.69, >=6.13.0 <6.18.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: wwan: t7xx: fix potential skb->frags overflow in RX path

When receiving data in the DPMAIF RX path,
the t7xx_dpmaif_set_frag_to_skb() function adds
page fragments to an skb without checking if the number of
fragments has exceeded MAX_SKB_FRAGS. This could lead to a buffer overflow
in skb_shinfo(skb)->frags[] array, corrupting adjacent memory and
potentially causing kernel crashes or other undefined behavior.

This issue was identified through static code analysis by comparing with a
similar vulnerability fixed in the mt76 driver commit b102f0c522cf ("mt76:
fix array overflow on receiving too many fragments for a packet").

The vulnerability could be triggered if the modem firmware sends packets
with excessive fragments. While under normal protocol conditions (MTU 3080
bytes, BAT buffer 3584 bytes),
a single packet should not require additional
fragments, the kernel should not blindly trust firmware behavior.
Malicious, buggy, or compromised firmware could potentially craft packets
with more fragments than the kernel expects.

Fix this by adding a bounds check before calling skb_add_rx_frag() to
ensure nr_frags does not exceed MAX_SKB_FRAGS.

The check must be performed before unmapping to avoid a page leak
and double DMA unmap during device teardown.

## References
- https://git.kernel.org/stable/c/2a0522f564acd34442652ea083091c329fa7c5d5
- https://git.kernel.org/stable/c/2c0fb0f60bc1545c52da61bc6bd4855c1e7814ba
- https://git.kernel.org/stable/c/af4b8577d0b388cc3d0039eb0cdd9ca5bbbc9276
- https://git.kernel.org/stable/c/f0813bcd2d9d97fdbdf2efb9532ab03ae92e99e6
- https://git.kernel.org/stable/c/f9747a7521a48afded5bff2faf1f2dcfff48c577
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23172.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23172
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
