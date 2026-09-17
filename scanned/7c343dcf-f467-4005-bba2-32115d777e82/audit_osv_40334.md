# [C] net: usb: rtl8150: fix use-after-free in rtl8150_start_xmit()

## Summary
Severity: Critical
Advisory: CVE-2026-52982
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52982
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: usb: rtl8150: fix use-after-free in rtl8150_start_xmit()

syzbot reported a KASAN slab-use-after-free read in rtl8150_start_xmit()
when accessing skb->len for tx statistics after usb_submit_urb() has
been called:

  BUG: KASAN: slab-use-after-free in rtl8150_start_xmit+0x71f/0x760
    drivers/net/usb/rtl8150.c:712
  Read of size 4 at addr ffff88810eb7a930 by task kworker/0:4/5226

The URB completion handler write_bulk_callback() frees the skb via
dev_kfree_skb_irq(dev->tx_skb). The URB may complete on another CPU
in softirq context before usb_submit_urb() returns in the submitter,
so by the time the submitter reads skb->len the skb has already been
queued to the per-CPU completion_queue and freed by net_tx_action():

  CPU A (xmit)                      CPU B (USB completion softirq)
  ------------                      ------------------------------
  dev->tx_skb = skb;
  usb_submit_urb()      --+
                          |-------> write_bulk_callback()
                          |           dev_kfree_skb_irq(dev->tx_skb)
                          |         net_tx_action()
                          |           napi_skb_cache_put()   <-- free
  netdev->stats.tx_bytes  |
    += skb->len;          <-- UAF read

Fix it by caching skb->len before submitting the URB and using the
cached value when updating the tx_bytes counter.

The pre-existing tx_bytes semantics are preserved: the counter tracks
the original frame length (skb->len), not the ETH_ZLEN/USB-alignment
padded "count" value that is handed to the device.  Changing that
would be a user-visible accounting change and is out of scope for
this UAF fix.

## References
- https://git.kernel.org/stable/c/23f0e34c64acba15cad4d23e50f41f533da195fa
- https://git.kernel.org/stable/c/24831b0b2ada9fef18d1f486b7b7c444ee5ba637
- https://git.kernel.org/stable/c/30cf9829d09ca958279c937af8e35495cd2f1e09
- https://git.kernel.org/stable/c/423b5b86e14e190f6e3161eb5f2ea5f908295ba7
- https://git.kernel.org/stable/c/4dd7eb94f79486b77ca6b4c8676aedbc465dc802
- https://git.kernel.org/stable/c/5af290c86fa81ddbc86a08d54229af5daa40c6a4
- https://git.kernel.org/stable/c/5db090ca07b28a63fb1499690cf19a3f3adafacb
- https://git.kernel.org/stable/c/6999d70e0eda39af029fa1891c48f0a8832b09d5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52982.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52982
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
