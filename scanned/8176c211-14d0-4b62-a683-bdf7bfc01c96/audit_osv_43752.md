# [H] net: tap: set skb->dev before parsing virtio net header in tap_get_user_xdp()

## Summary
Severity: High
Advisory: CVE-2026-74684
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74684
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <6.12.105, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: tap: set skb->dev before parsing virtio net header in tap_get_user_xdp()

The commit 4f61f133f354 ("net: tap: NULL pointer derefence in
dev_parse_header_protocol when skb->dev is null") fixed a crash in
tap_get_user() by assigning skb->dev before calling tun_vnet_hdr_to_skb().
This is required because virtio_net_hdr_to_skb() may invoke
dev_parse_header_protocol(), which dereferences skb->dev. Without the
assignment, a NULL pointer dereference can occur.

However, tap_get_user_xdp() still parses the virtio-net header before
assigning skb->dev. When the vhost TX path passes an XDP buffer containing
a GSO virtio-net header but the protocol is set to zero on purpose,
tun_vnet_hdr_to_skb() can reach dev_parse_header_protocol() while skb->dev
is still NULL, resulting in a crash.

Fix this by looking up the tap device and assigning skb->dev before calling
tun_vnet_hdr_to_skb(), matching the ordering already used in
tap_get_user(). Preserve the existing RCU read-side critical section across
dev_queue_xmit().

## References
- https://git.kernel.org/stable/c/15583b07fd691a844fbf7b3ad612cdc9e9a657c0
- https://git.kernel.org/stable/c/164c31ee252ebd1ac8f44c2dfc5486b6d9a0379b
- https://git.kernel.org/stable/c/3874892dd27d5387aa9a06f58d9060f18f351d24
- https://git.kernel.org/stable/c/8b444b126cd8e4473e652f529753ed4dd1360a9c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74684.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74684
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
