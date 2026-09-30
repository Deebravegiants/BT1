# [M] vsock: Update rx_bytes on read_skb()

## Summary
Severity: Medium
Advisory: CVE-2024-50169
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50169
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock: Update rx_bytes on read_skb()

Make sure virtio_transport_inc_rx_pkt() and virtio_transport_dec_rx_pkt()
calls are balanced (i.e. virtio_vsock_sock::rx_bytes doesn't lie) after
vsock_transport::read_skb().

While here, also inform the peer that we've freed up space and it has more
credit.

Failing to update rx_bytes after packet is dequeued leads to a warning on
SOCK_STREAM recv():

[  233.396654] rx_queue is empty, but rx_bytes is non-zero
[  233.396702] WARNING: CPU: 11 PID: 40601 at net/vmw_vsock/virtio_transport_common.c:589

## References
- https://git.kernel.org/stable/c/3543152f2d330141d9394d28855cb90b860091d2
- https://git.kernel.org/stable/c/66cd51de31c682a311c2fa25c580b7ea45859dd9
- https://git.kernel.org/stable/c/e5ca2b98090b4bb1c393088c724af6c37812a829
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50169.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50169
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
