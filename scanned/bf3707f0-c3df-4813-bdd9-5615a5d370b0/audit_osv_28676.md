# [C] udp: do not accept non-tunnel GSO skbs landing in a tunnel

## Summary
Severity: Critical
Advisory: CVE-2024-35884
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35884
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

udp: do not accept non-tunnel GSO skbs landing in a tunnel

When rx-udp-gro-forwarding is enabled UDP packets might be GROed when
being forwarded. If such packets might land in a tunnel this can cause
various issues and udp_gro_receive makes sure this isn't the case by
looking for a matching socket. This is performed in
udp4/6_gro_lookup_skb but only in the current netns. This is an issue
with tunneled packets when the endpoint is in another netns. In such
cases the packets will be GROed at the UDP level, which leads to various
issues later on. The same thing can happen with rx-gro-list.

We saw this with geneve packets being GROed at the UDP level. In such
case gso_size is set; later the packet goes through the geneve rx path,
the geneve header is pulled, the offset are adjusted and frag_list skbs
are not adjusted with regard to geneve. When those skbs hit
skb_fragment, it will misbehave. Different outcomes are possible
depending on what the GROed skbs look like; from corrupted packets to
kernel crashes.

One example is a BUG_ON[1] triggered in skb_segment while processing the
frag_list. Because gso_size is wrong (geneve header was pulled)
skb_segment thinks there is "geneve header size" of data in frag_list,
although it's in fact the next packet. The BUG_ON itself has nothing to
do with the issue. This is only one of the potential issues.

Looking up for a matching socket in udp_gro_receive is fragile: the
lookup could be extended to all netns (not speaking about performances)
but nothing prevents those packets from being modified in between and we
could still not find a matching socket. It's OK to keep the current
logic there as it should cover most cases but we also need to make sure
we handle tunnel packets being GROed too early.

This is done by extending the checks in udp_unexpected_gso: GSO packets
lacking the SKB_GSO_UDP_TUNNEL/_CSUM bits and landing in a tunnel must
be segmented.

[1] kernel BUG at net/core/skbuff.c:4408!
    RIP: 0010:skb_segment+0xd2a/0xf70
    __udp_gso_segment+0xaa/0x560

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/3001e7aa43d6691db2a878b0745b854bf12ddd19
- https://git.kernel.org/stable/c/3391b157780bbedf8ef9f202cbf10ee90bf6b0f8
- https://git.kernel.org/stable/c/35fe0e0b5c00bef7dde74842a2564c43856fbce4
- https://git.kernel.org/stable/c/3d010c8031e39f5fa1e8b13ada77e0321091011f
- https://git.kernel.org/stable/c/d12245080cb259d82b34699f6cd4ec11bdb688bd
- https://git.kernel.org/stable/c/d49ae15a5767d4e9ef8bbb79e42df1bfebc94670
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35884.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35884
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
