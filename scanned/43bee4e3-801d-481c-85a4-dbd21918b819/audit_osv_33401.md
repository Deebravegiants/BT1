# [H] Bluetooth: 6lowpan: reset link-local header on ipv6 recv path

## Summary
Severity: High
Advisory: CVE-2025-40282
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-06
Source: https://osv.dev/vulnerability/CVE-2025-40282
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <5.4.302, >=5.5.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.59, >=6.13.0 <6.17.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: 6lowpan: reset link-local header on ipv6 recv path

Bluetooth 6lowpan.c netdev has header_ops, so it must set link-local
header for RX skb, otherwise things crash, eg. with AF_PACKET SOCK_RAW

Add missing skb_reset_mac_header() for uncompressed ipv6 RX path.

For the compressed one, it is done in lowpan_header_decompress().

Log: (BlueZ 6lowpan-tester Client Recv Raw - Success)
------
kernel BUG at net/core/skbuff.c:212!
Call Trace:
<IRQ>
...
packet_rcv (net/packet/af_packet.c:2152)
...
<TASK>
__local_bh_enable_ip (kernel/softirq.c:407)
netif_rx (net/core/dev.c:5648)
chan_recv_cb (net/bluetooth/6lowpan.c:294 net/bluetooth/6lowpan.c:359)
------

## References
- https://git.kernel.org/stable/c/11cd7e068381666f842ad41d1cc58eecd0c75237
- https://git.kernel.org/stable/c/3b78f50918276ab28fb22eac9aa49401ac436a3b
- https://git.kernel.org/stable/c/4ebb90c3c309e6375dc3e841af92e2a039843e62
- https://git.kernel.org/stable/c/70d84e7c3a44b81020a3c3d650a64c63593405bd
- https://git.kernel.org/stable/c/973e0271754c77db3e1b6b69adf2de85a79a4c8b
- https://git.kernel.org/stable/c/c24ac6cfe4f9a47180a65592c47e7a310d2f9d93
- https://git.kernel.org/stable/c/d566e9a2bfc848941b091ffd5f4e12c4e889d818
- https://git.kernel.org/stable/c/ea46a1d217bc82e01cf3d0424e50ebfe251e34bf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40282.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40282
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
