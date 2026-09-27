# [H] usbnet: gl620a: fix out-of-bounds read in genelink_rx_fixup()

## Summary
Severity: High
Advisory: CVE-2026-64540
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64540
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.14 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

usbnet: gl620a: fix out-of-bounds read in genelink_rx_fixup()

genelink_rx_fixup() splits an aggregated RX frame into its individual
packets, using a per-packet length taken from device-supplied data. That
length is only bounded by GL_MAX_PACKET_LEN (1514); it is never compared
against how many bytes were actually received.

A malicious GeneLink (GL620A) device can therefore send a short URB whose
header claims packet_count > 1 and a first packet of up to 1514 bytes.

	skb_put_data(gl_skb, packet->packet_data, size);

then copies past the end of the receive buffer and hands the adjacent slab
contents up the network stack, an out-of-bounds read that leaks kernel heap.
No privilege is required: the path runs in the usbnet RX softirq as soon as
the interface is up.

  BUG: KASAN: slab-out-of-bounds in genelink_rx_fixup (drivers/net/usb/gl620a.c:112)
  Read of size 1514 at addr ffff888011309708 by task ksoftirqd/0/14
  Call Trace:
    ...
    __asan_memcpy (mm/kasan/shadow.c:105)
    genelink_rx_fixup (include/linux/skbuff.h:2814 drivers/net/usb/gl620a.c:112)
    usbnet_bh (drivers/net/usb/usbnet.c:572 drivers/net/usb/usbnet.c:1589)
    process_one_work (kernel/workqueue.c:3322)
    bh_worker (kernel/workqueue.c:3405)
    tasklet_action (kernel/softirq.c:965)
    handle_softirqs (kernel/softirq.c:622)
    run_ksoftirqd (kernel/softirq.c:1076)
    ...

skb_pull() already verifies that the requested length fits the buffer and
returns NULL otherwise. Move it ahead of the copy and check its result, so
a packet that overruns the received data is rejected before it is read.
Well-formed frames, whose packets are fully present, are unaffected.

## References
- https://git.kernel.org/stable/c/0575599e451aff3c5329922562374a2cab25fc51
- https://git.kernel.org/stable/c/0a7d9c7c5f1f208c523abbb4db6aea7bc1fad3db
- https://git.kernel.org/stable/c/255d03551f94c7bdd86c7d9181a70b21917d829f
- https://git.kernel.org/stable/c/3ef79fa3860e644c8de7834fa7300e1c58f38862
- https://git.kernel.org/stable/c/4359376e6238d89977a35086e47ca3b07f43e850
- https://git.kernel.org/stable/c/573418f7ea8f859a841417eb4b915594094fd967
- https://git.kernel.org/stable/c/8624e179fa3ce23c2fbd1a198ce30764b73f054a
- https://git.kernel.org/stable/c/8ff7f2a6da4fccaa5cc9be7251a24e71e29fbd1a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64540.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64540
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
