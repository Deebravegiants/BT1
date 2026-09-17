# [H] vsock/virtio: Validate length in packet header before skb_put()

## Summary
Severity: High
Advisory: CVE-2025-39718
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39718
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.149, >=6.2.0 <6.6.103, >=6.3.0 <6.12.44, >=6.7.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock/virtio: Validate length in packet header before skb_put()

When receiving a vsock packet in the guest, only the virtqueue buffer
size is validated prior to virtio_vsock_skb_rx_put(). Unfortunately,
virtio_vsock_skb_rx_put() uses the length from the packet header as the
length argument to skb_put(), potentially resulting in SKB overflow if
the host has gone wonky.

Validate the length as advertised by the packet header before calling
virtio_vsock_skb_rx_put().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/0dab92484474587b82e8e0455839eaf5ac7bf894
- https://git.kernel.org/stable/c/676f03760ca1d69c2470cef36c44dc152494b47c
- https://git.kernel.org/stable/c/969b06bd8b7560efb100a34227619e7d318fbe05
- https://git.kernel.org/stable/c/ee438c492b2e0705d819ac0e25d04fae758d8f8f
- https://git.kernel.org/stable/c/faf332a10372390ce65d0b803888f4b25a388335
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39718.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39718
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
