# [H] net: usb: net1080: validate packet_len before pad-byte access in rx_fixup

## Summary
Severity: High
Advisory: CVE-2026-64547
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64547
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.14 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: usb: net1080: validate packet_len before pad-byte access in rx_fixup

For an even packet_len, net1080_rx_fixup() reads the pad byte at
skb->data[packet_len] before the skb->len != packet_len check further
down, and packet_len is only bounded against NC_MAX_PACKET. A malicious
NetChip 1080 device can send a short frame advertising a large even
packet_len (e.g. 0x4000), so the pad-byte read lands past the end of the
skb:

  BUG: KASAN: slab-out-of-bounds in net1080_rx_fixup
  Read of size 1 at addr ffff8880106c83c6 by task ksoftirqd/0/14
   ...
   net1080_rx_fixup (drivers/net/usb/net1080.c:384)
   usbnet_bh (drivers/net/usb/usbnet.c:1589)
   process_one_work (kernel/workqueue.c:3322)
   bh_worker (kernel/workqueue.c:3708)
   tasklet_action (kernel/softirq.c:965)
   handle_softirqs (kernel/softirq.c:622)
   ...

Reject the frame when packet_len >= skb->len before reading.

## References
- https://git.kernel.org/stable/c/03f384bc0cb8d4a1301d4f5b0baef2d980258383
- https://git.kernel.org/stable/c/4dc8484be3302d187274364820d3bef6c62bde32
- https://git.kernel.org/stable/c/685e92934f11d5e215dad58813e2f9955ac2f436
- https://git.kernel.org/stable/c/b153cfe84b1340c69a13d0957665a2bfcf21239c
- https://git.kernel.org/stable/c/c087749815379e9af2fdbeb08bfc33870b103958
- https://git.kernel.org/stable/c/e4a87126c085b097d29e17e3b7647295bba8be7c
- https://git.kernel.org/stable/c/ea866cab12db1a2100b400a8b03569e5bc0ee29a
- https://git.kernel.org/stable/c/f42217fa7d535e9ec4151f7971f06f6ea65e850a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64547.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64547
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
