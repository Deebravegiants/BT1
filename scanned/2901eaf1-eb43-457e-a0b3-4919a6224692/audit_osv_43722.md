# [H] NTB: ntb_netdev: Preserve RX queue depth on allocation failure

## Summary
Severity: High
Advisory: CVE-2026-74626
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74626
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <5.10.267, >=5.11.0 <5.15.218, >=5.16.0 <6.1.185, >=6.2.0 <6.6.154, >=6.7.0 <6.12.106, >=6.13.0 <6.18.46, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

NTB: ntb_netdev: Preserve RX queue depth on allocation failure

ntb_netdev_rx_handler() hands the received skb to the network stack
before allocating its replacement. If the allocation fails, nothing is
reposted. Every failure therefore takes one buffer out of the RX queue
while the interface remains up, and enough failures eventually stall
reception.

A retry path could refill the queue later, but ntb_netdev has none.
Allocate the replacement first instead. If that fails, drop the packet
and repost the same skb. This keeps the queue full and lets packet
delivery resume as soon as memory is available again.

## References
- https://git.kernel.org/stable/c/18781cc0bfb5c7f2a51ac6d678a28f101b7c35c5
- https://git.kernel.org/stable/c/272df0fbe6f3e04e22bc67fbdd9ac24586b942f4
- https://git.kernel.org/stable/c/3f2a15f33f86f7bd5b920669fd40c06725d72a1e
- https://git.kernel.org/stable/c/6d7f8a23c130d768c0976c2578b214353674e18f
- https://git.kernel.org/stable/c/755fd7843f300d724caceabdf9bb13adc8701540
- https://git.kernel.org/stable/c/a4e340971fe8ccd245d206db4d43b2a0eec240bd
- https://git.kernel.org/stable/c/d2121faf133ac3bf9531b53a7e21273649a08517
- https://git.kernel.org/stable/c/fcaf8ba7e56bb73319ac107a63b907d59536192c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74626.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74626
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
