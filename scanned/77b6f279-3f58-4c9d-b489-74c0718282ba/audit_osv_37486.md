# [H] net/packet: fix TOCTOU race on mmap'd vnet_hdr in tpacket_snd()

## Summary
Severity: High
Advisory: CVE-2026-31700
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31700
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.136, >=6.7.0 <6.12.84, >=6.13.0 <6.18.25, >=6.19.0 <7.0.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/packet: fix TOCTOU race on mmap'd vnet_hdr in tpacket_snd()

In tpacket_snd(), when PACKET_VNET_HDR is enabled, vnet_hdr points
directly into the mmap'd TX ring buffer shared with userspace. The
kernel validates the header via __packet_snd_vnet_parse() but then
re-reads all fields later in virtio_net_hdr_to_skb(). A concurrent
userspace thread can modify the vnet_hdr fields between validation
and use, bypassing all safety checks.

The non-TPACKET path (packet_snd()) already correctly copies vnet_hdr
to a stack-local variable. All other vnet_hdr consumers in the kernel
(tun.c, tap.c, virtio_net.c) also use stack copies. The TPACKET TX
path is the only caller of virtio_net_hdr_to_skb() that reads directly
from user-controlled shared memory.

Fix this by copying vnet_hdr from the mmap'd ring buffer to a
stack-local variable before validation and use, consistent with the
approach used in packet_snd() and all other callers.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/0f4c9754956b86de158a4af5278c5cf5bda9439e
- https://git.kernel.org/stable/c/1490f82353bdabc09265a74e645b07f05cf4188e
- https://git.kernel.org/stable/c/28324a3b62d9ce7f9bdd65a8ce63f382041d1b27
- https://git.kernel.org/stable/c/2c054e17d9d41f1020376806c7f750834ced4dc5
- https://git.kernel.org/stable/c/3a1bf9116ea31470b89692585c3910dfe830dcdd
- https://git.kernel.org/stable/c/48a6ef291a17639e1b6ae0fbe9c8b2bb87d7804b
- https://git.kernel.org/stable/c/714aa973da8163925eda7efd49361ccbee21ee46
- https://git.kernel.org/stable/c/74e2db36fe50e3ad9d5300d7fd0e6e2a15a6d121
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31700.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31700
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
