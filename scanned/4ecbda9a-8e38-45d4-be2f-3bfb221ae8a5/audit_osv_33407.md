# [H] virtio-net: fix received length check in big packets

## Summary
Severity: High
Advisory: CVE-2025-40292
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-40292
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio-net: fix received length check in big packets

Since commit 4959aebba8c0 ("virtio-net: use mtu size as buffer length
for big packets"), when guest gso is off, the allocated size for big
packets is not MAX_SKB_FRAGS * PAGE_SIZE anymore but depends on
negotiated MTU. The number of allocated frags for big packets is stored
in vi->big_packets_num_skbfrags.

Because the host announced buffer length can be malicious (e.g. the host
vhost_net driver's get_rx_bufs is modified to announce incorrect
length), we need a check in virtio_net receive path. Currently, the
check is not adapted to the new change which can lead to NULL page
pointer dereference in the below while loop when receiving length that
is larger than the allocated one.

This commit fixes the received length check corresponding to the new
change.

## References
- https://git.kernel.org/stable/c/0c716703965ffc5ef4311b65cb5d84a703784717
- https://git.kernel.org/stable/c/3e9d89f2ecd3636bd4cbdfd0b2dfdaf58f9882e2
- https://git.kernel.org/stable/c/82f9028e83944a9eee5229cbc6fee9be1de8a62d
- https://git.kernel.org/stable/c/82fe78065450d2d07f36a22e2b6b44955cf5ca5b
- https://git.kernel.org/stable/c/946dec89c41726b94d31147ec528b96af0be1b5a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40292.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40292
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
