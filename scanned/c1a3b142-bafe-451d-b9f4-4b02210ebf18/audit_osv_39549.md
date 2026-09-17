# [H] Bluetooth: virtio_bt: clamp rx length before skb_put

## Summary
Severity: High
Advisory: CVE-2026-46123
Ecosystem: Linux
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46123
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.209, >=5.16.0 <6.1.175, >=6.1.0 <6.6.140, >=6.2.0 <6.12.88, >=6.7.0 <6.18.30, >=6.13.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: virtio_bt: clamp rx length before skb_put

virtbt_rx_work() calls skb_put(skb, len) where len comes directly
from virtqueue_get_buf() with no validation against the buffer we
posted to the device. The RX skb is allocated in virtbt_add_inbuf()
and exposed to virtio as exactly 1000 bytes via sg_init_one().

Checking len against skb_tailroom(skb) is not sufficient because
alloc_skb() can leave more tailroom than the 1000 bytes actually
handed to the device. A malicious or buggy backend can therefore
report used.len between 1001 and skb_tailroom(skb), causing skb_put()
to include uninitialized kernel heap bytes that were never written by
the device.

The same path also accepts len == 0, in which case skb_put(skb, 0)
leaves the skb empty but virtbt_rx_handle() still reads the pkt_type
byte from skb->data, consuming uninitialized memory.

Define VIRTBT_RX_BUF_SIZE once and reuse it in alloc_skb() and
sg_init_one(), and gate virtbt_rx_work() on that same constant so
the bound checked matches the buffer actually exposed to the device.
Reject used.len == 0 in the same gate so an empty completion can
no longer reach virtbt_rx_handle().

Use bt_dev_err_ratelimited() because the length value comes from an
untrusted backend that can otherwise flood the kernel log.

Same class of bug as commit c04db81cd028 ("net/9p: Fix buffer
overflow in USB transport layer"), which hardened the USB 9p
transport against unchecked device-reported length.

## References
- https://git.kernel.org/stable/c/21bd244b6de5d2fe1063c23acc93fbdd2b20d112
- https://git.kernel.org/stable/c/4236e55b2d9d1ffd3b4bdf8ebbb86e5a0a526b4a
- https://git.kernel.org/stable/c/6c1730099a6fc18b183bd6c1adad3b54adcaeda9
- https://git.kernel.org/stable/c/b40cdd1b1370d76e9e760af4490cb4a351cceead
- https://git.kernel.org/stable/c/e6b4296f170d949ebba937cf6a3f247ec9550d2c
- https://git.kernel.org/stable/c/ed41c81d30b211a671667259c3b5feeba0e062d5
- https://git.kernel.org/stable/c/fd91fa2678ab603dfb285416c1cf3843d7be1e41
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46123.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46123
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
