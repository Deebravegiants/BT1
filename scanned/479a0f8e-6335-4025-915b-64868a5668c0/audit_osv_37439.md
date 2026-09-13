# [C] usbip: validate number_of_packets in usbip_pack_ret_submit()

## Summary
Severity: Critical
Advisory: CVE-2026-31607
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31607
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

usbip: validate number_of_packets in usbip_pack_ret_submit()

When a USB/IP client receives a RET_SUBMIT response,
usbip_pack_ret_submit() unconditionally overwrites
urb->number_of_packets from the network PDU. This value is
subsequently used as the loop bound in usbip_recv_iso() and
usbip_pad_iso() to iterate over urb->iso_frame_desc[], a flexible
array whose size was fixed at URB allocation time based on the
*original* number_of_packets from the CMD_SUBMIT.

A malicious USB/IP server can set number_of_packets in the response
to a value larger than what was originally submitted, causing a heap
out-of-bounds write when usbip_recv_iso() writes to
urb->iso_frame_desc[i] beyond the allocated region.

KASAN confirmed this with kernel 7.0.0-rc5:

  BUG: KASAN: slab-out-of-bounds in usbip_recv_iso+0x46a/0x640
  Write of size 4 at addr ffff888106351d40 by task vhci_rx/69

  The buggy address is located 0 bytes to the right of
   allocated 320-byte region [ffff888106351c00, ffff888106351d40)

The server side (stub_rx.c) and gadget side (vudc_rx.c) already
validate number_of_packets in the CMD_SUBMIT path since commits
c6688ef9f297 ("usbip: fix stub_rx: harden CMD_SUBMIT path to handle
malicious input") and b78d830f0049 ("usbip: fix vudc_rx: harden
CMD_SUBMIT path to handle malicious input"). The server side validates
against USBIP_MAX_ISO_PACKETS because no URB exists yet at that point.
On the client side we have the original URB, so we can use the tighter
bound: the response must not exceed the original number_of_packets.

This mirrors the existing validation of actual_length against
transfer_buffer_length in usbip_recv_xbuff(), which checks the
response value against the original allocation size.

Kelvin Mbogo's series ("usb: usbip: fix integer overflow in
usbip_recv_iso()", v2) hardens the receive-side functions themselves;
this patch complements that work by catching the bad value at its
source -- in usbip_pack_ret_submit() before the overwrite -- and
using the tighter per-URB allocation bound rather than the global
USBIP_MAX_ISO_PACKETS limit.

Fix this by checking rpdu->number_of_packets against
urb->number_of_packets in usbip_pack_ret_submit() before the
overwrite. On violation, clamp to zero so that usbip_recv_iso() and
usbip_pad_iso() safely return early.

## References
- https://git.kernel.org/stable/c/2ab833a16a825373aad2ba7d54b572b277e95b71
- https://git.kernel.org/stable/c/324262c38438255bf6bdbf6342ca47c0badaab76
- https://git.kernel.org/stable/c/5e1c4ece08ccdc197177631f111845a2c68eede3
- https://git.kernel.org/stable/c/885c8591784da6314f9aa82fa460ac69f9f79e5f
- https://git.kernel.org/stable/c/8d155e2d1c4102f74f82a2bf9c016164bb0f7384
- https://git.kernel.org/stable/c/906f16a836de13fe61f49cdce2f66f2dbd14caf4
- https://git.kernel.org/stable/c/973f2c250289f5bf6cc146b98aa6fdde11fe50d6
- https://git.kernel.org/stable/c/ce744264b06b97069b3722511ab355738311fee0
- https://git.kernel.org/stable/c/ef8ebb1c637b4cfb61a9dd2e013376774ee2033b
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-31607.json
- https://access.redhat.com/errata/RHSA-2026:19568
- https://access.redhat.com/errata/RHSA-2026:19569
- https://access.redhat.com/errata/RHSA-2026:23224
- https://access.redhat.com/errata/RHSA-2026:24343
- https://access.redhat.com/errata/RHSA-2026:25095
- https://access.redhat.com/errata/RHSA-2026:41236
- https://access.redhat.com/security/cve/CVE-2026-31607
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31607.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31607
- https://bugzilla.redhat.com/show_bug.cgi?id=2461521
